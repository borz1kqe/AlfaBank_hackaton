# src/services/rag_store.py
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

from src.models.schemas import BankResearchChunk, CompanyContext, NewsItem
from src.services.context_builder import ClientContextBuilder
from src.services.news_parser import NewsParserService
from src.services.synthetic_generator import SyntheticDataGenerator


class LocalBM25Index:
    """Легковесный Okapi BM25 с поддержкой русской морфологической нормализации (основы слов)."""

    def __init__(self, documents: List[str], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.doc_tokens: List[List[str]] = [self.tokenize(doc) for doc in documents]
        self.doc_freqs: List[Counter[str]] = [Counter(toks) for toks in self.doc_tokens]
        self.doc_lens: List[int] = [len(toks) for toks in self.doc_tokens]
        self.avgdl: float = (
            sum(self.doc_lens) / len(self.doc_lens) if self.doc_lens else 1.0
        )
        self.n_docs = len(documents)
        self.idf: Dict[str, float] = self._compute_idf()

    @staticmethod
    def tokenize(text: str) -> List[str]:
        words = re.findall(r"[а-яa-z0-9.]{2,}", (text or "").lower())
        # Легкий стемминг русских окончаний для высокого recall без внешних словарей
        stems: List[str] = []
        for w in words:
            if len(w) > 6:
                stems.append(w[:6])
            else:
                stems.append(w)
        return stems

    def _compute_idf(self) -> Dict[str, float]:
        df_counts: Counter[str] = Counter()
        for freqs in self.doc_freqs:
            for token in freqs.keys():
                df_counts[token] += 1
        idf: Dict[str, float] = {}
        for token, df in df_counts.items():
            idf[token] = math.log(1.0 + (self.n_docs - df + 0.5) / (df + 0.5))
        return idf

    def score_all(self, query: str) -> List[float]:
        q_tokens = self.tokenize(query)
        scores = [0.0] * self.n_docs
        for idx in range(self.n_docs):
            dl = self.doc_lens[idx]
            freqs = self.doc_freqs[idx]
            s = 0.0
            for qt in q_tokens:
                tf = freqs.get(qt, 0)
                if tf == 0:
                    continue
                idf_val = self.idf.get(qt, 0.0)
                denom = tf + self.k1 * (1.0 - self.b + self.b * (dl / max(self.avgdl, 1.0)))
                s += idf_val * (tf * (self.k1 + 1.0)) / denom
            scores[idx] = s
        return scores


class AlfaRAGStore:
    """Единый фасад данных и RAG-поиска для AI-агента (Роль 2)."""

    def __init__(
        self,
        uid_csv_path: str = "data/raw/df_Uid_data_hack.csv",
        fid_csv_path: str = "data/raw/df_Fid_Uid_link_hack.csv",
        news_path: str = "data/raw/news_feed.json",
        analytics_path: str = "data/bank_analytics/bank_research.json",
    ) -> None:
        self.news_path = Path(news_path)
        self.analytics_path = Path(analytics_path)

        if not self.news_path.exists() or not self.analytics_path.exists():
            SyntheticDataGenerator().generate_all(overwrite=False)

        self.context_builder = ClientContextBuilder(
            uid_csv_path=uid_csv_path,
            fid_csv_path=fid_csv_path,
            auto_generate_if_missing=True,
        )
        self.news_parser = NewsParserService()
        self.news_items: List[NewsItem] = self.news_parser.load_from_json_or_csv(
            self.news_path
        )
        self.analytics_chunks: List[BankResearchChunk] = self._load_analytics(
            self.analytics_path
        )

        # Строим BM25 индексы
        self._news_bm25 = LocalBM25Index(
            [
                f"{n.title} {n.raw_text} {' '.join(n.tags)} {' '.join(n.affected_okveds)}"
                for n in self.news_items
            ]
        )
        self._analytics_bm25 = LocalBM25Index(
            [
                f"{c.report_title} {c.topic} {c.key_thesis} {c.content}"
                for c in self.analytics_chunks
            ]
        )

    @staticmethod
    def _load_analytics(path: Path) -> List[BankResearchChunk]:
        with open(path, "r", encoding="utf-8") as f:
            raw_chunks = json.load(f)
        return [BankResearchChunk(**chunk) for chunk in raw_chunks]

    # -------------------- 1. ПРОФИЛЬ КОМПАНИИ --------------------

    def get_company_context(self, synthetic_u: str) -> CompanyContext:
        """Возвращает полный CompanyContext по ID компании."""
        return self.context_builder.build_context(synthetic_u)

    # -------------------- 2. ПОИСК РЕЛЕВАНТНЫХ НОВОСТЕЙ --------------------

    def search_relevant_news(
        self, company_ctx: CompanyContext, role: str = "relationship_manager", top_k: int = 5
    ) -> List[NewsItem]:
        """Ищет новости с учетом:
        1) Прямого ОКВЭД компании и ОКВЭД её группы (GROUP_ID)
        2) Косвенного влияния через ОКВЭД топ-поставщиков и топ-покупателей
        3) Макро-профиля (долг/ставка ЦБ, депозиты, страны ВЭД, штат сотрудников)
        4) Роли пользователя (risk_manager / relationship_manager / cfo)
        """
        counterparty_okveds = {cp.okved_code for cp in company_ctx.top_counterparties}
        group_okved_codes = {
            okv.split()[0].strip() for okv in company_ctx.group_context.group_okveds
        }

        query_parts = [
            company_ctx.main_okved_code,
            company_ctx.main_okved_name,
            " ".join(company_ctx.fts_countries),
            " ".join(company_ctx.active_products),
            " ".join(company_ctx.risk_sensitivity_factors),
            " ".join(cp.okved_name for cp in company_ctx.top_counterparties),
        ]
        bm25_scores = self._news_bm25.score_all(" ".join(query_parts))

        role_low = (role or "").lower()
        scored_news: List[tuple[float, NewsItem]] = []

        for idx, news in enumerate(self.news_items):
            score = bm25_scores[idx]
            news_okveds = set(news.affected_okveds)
            triggers = set(news.macro_triggers)

            # A. Прямое попадание в основной ОКВЭД компании (+12 баллов)
            if company_ctx.main_okved_code in news_okveds:
                score += 12.0
            # B. Попадание в ОКВЭД группы компаний (+5 баллов)
            elif news_okveds & group_okved_codes:
                score += 5.0

            # C. Косвенное попадание через цепочку поставок (топ-поставщики и покупатели) (+7 баллов)
            if news_okveds & counterparty_okveds:
                score += 7.0

            # D. Бустинг по странам ВЭД (+6 баллов)
            if company_ctx.is_foreign_trade and "fx_customs" in triggers:
                score += 4.0
                for country in company_ctx.fts_countries:
                    if country.lower()[:4] in news.raw_text.lower():
                        score += 4.0

            # E. Процентный риск (кредиты/лизинг) или избыточная ликвидность (депозиты)
            has_debt = (
                "Кредитование" in company_ctx.active_products
                or "Лизинг" in company_ctx.active_products
            )
            if has_debt and ("key_rate" in triggers or "bonds_liquidity" in triggers):
                score += 5.0
            if (
                "Депозиты" in company_ctx.active_products
                and not has_debt
                and ("key_rate" in triggers or "bonds_liquidity" in triggers)
            ):
                score += 5.0

            # F. Учет роли (персонализация выдачи)
            if "risk" in role_low or "риск" in role_low:
                if triggers & {"key_rate", "supply_chain", "taxes_regulation", "fx_customs"}:
                    score += 3.0
            elif "rm" in role_low or "manager" in role_low or "менеджер" in role_low:
                if triggers & {"consumption", "commodities_gold", "bonds_liquidity", "fx_customs"}:
                    score += 3.0

            scored_news.append((score, news))

        scored_news.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored_news[:top_k]]

    # -------------------- 3. ПОИСК ПО 9 МАКРО-ОТЧЕТАМ АЛЬФА-БАНКА --------------------

    def search_bank_analytics(
        self, query: str, triggers: Optional[List[str]] = None, top_k: int = 3
    ) -> List[BankResearchChunk]:
        """Возвращает топ-K аналитических чанков из 9 макро-отчетов Альфа-Банка
        для подтверждения выводов агента.
        """
        triggers_set = set(triggers or [])
        expanded_query = f"{query} {' '.join(triggers_set)}"
        bm25_scores = self._analytics_bm25.score_all(expanded_query)

        scored_chunks: List[tuple[float, BankResearchChunk]] = []
        for idx, chunk in enumerate(self.analytics_chunks):
            score = bm25_scores[idx]

            # Бустинг при совпадении темы отчета с макро-триггерами новости/компании
            if chunk.topic in triggers_set:
                score += 8.0
            if chunk.topic == "macro_strategy" and (
                {"key_rate", "bonds_liquidity"} & triggers_set
            ):
                score += 4.5
            if chunk.topic == "gdp_macro" and (
                {"supply_chain", "inflation"} & triggers_set
            ):
                score += 4.0

            scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored_chunks[:top_k]]
