# src/services/news_parser.py
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set, Any
import pandas as pd

from src.models.schemas import NewsItem


MACRO_TRIGGER_RULES: Dict[str, List[str]] = {
    "key_rate": ["ключев", "ставк", "цб рф", "банк россии", "дкп", "14,0%", "14%", "рефинансир"],
    "inflation": ["инфляц", "рост цен", "удорожан", "тариф", "индексац", "издерж"],
    "fx_customs": [
        "вэд", "экспорт", "импорт", "тамож", "кита", "оаэ", "инди", "египет",
        "юан", "валют", "трансгранич", "пошлин", "погранпереход", "кнр",
    ],
    "commodities_gold": ["золот", "драгметалл", "сырь", "металлург", "котировк", "полимер", "масел"],
    "labor_market": ["кадр", "рынок труда", "зарплат", "фот", "персонал", "работодател", "водител", "разработчик"],
    "consumption": ["потреблен", "розничн", "ритейл", "трафик", "сберегательн", "торговые сети", "отсрочк"],
    "bonds_liquidity": ["облигац", "бонд", "офз", "флоатер", "спред", "депозит", "ликвидност", "овернайт"],
    "supply_chain": ["логист", "перевозк", "цепоч", "поставщик", "подрядчик", "лизинг", "кассовых разрыв"],
    "taxes_regulation": ["фнс", "налог", "субсид", "минцифр", "комплаенс", "квот"],
}

OKVED_KEYWORD_RULES: Dict[str, List[str]] = {
    "24.41": ["24.41", "золот", "драгоценных металлов", "металлург"],
    "47.11": ["47.11", "розничн", "ритейл", "торговые сети", "дискаунтер"],
    "49.41": ["49.41", "грузоперевоз", "автоперевоз", "логист", "тягач", "грузового транспорта"],
    "41.20": ["41.20", "строитель", "застройщик", "недвижимост", "подрядчик"],
    "62.01": ["62.01", "программного обеспечения", "разработчик", "облачн", "it-", "ии "],
    "10.41": ["10.41", "масел", "жиров", "подсолнечн", "рапсов", "агро"],
    "20.16": ["20.16", "пластмасс", "полимер", "синтетических смол", "спецхим", "упаковк"],
}


class NewsParserService:
    """Парсер внешних новостей (JSON/CSV/RSS/HTML) с дедупликацией
    и автоматическим извлечением макро-триггеров и ОКВЭД.
    """

    @staticmethod
    def _clean_html(text: str) -> str:
        no_tags = re.sub(r"<[^>]+>", " ", text or "")
        return re.sub(r"\s+", " ", no_tags).strip()

    @staticmethod
    def _tokenize(text: str) -> Set[str]:
        return {w for w in re.findall(r"[а-яa-z0-9]{4,}", text.lower())}

    def _is_duplicate(
        self, title: str, text: str, seen_hashes: Set[str], seen_token_sets: List[Set[str]]
    ) -> bool:
        norm_title = re.sub(r"[^а-яa-z0-9]", "", title.lower())
        h = hashlib.md5(norm_title.encode("utf-8")).hexdigest()
        if h in seen_hashes:
            return True

        tokens = self._tokenize(f"{title} {text}")
        for prev_tokens in seen_token_sets:
            if not tokens or not prev_tokens:
                continue
            jaccard = len(tokens & prev_tokens) / float(len(tokens | prev_tokens))
            if jaccard >= 0.75:
                return True

        seen_hashes.add(h)
        seen_token_sets.append(tokens)
        return False

    def extract_macro_triggers(self, full_text: str) -> List[str]:
        low = full_text.lower()
        triggers = [
            trig
            for trig, keywords in MACRO_TRIGGER_RULES.items()
            if any(kw in low for kw in keywords)
        ]
        return triggers or ["general_macro"]

    def extract_affected_okveds(self, full_text: str) -> List[str]:
        low = full_text.lower()
        okveds: Set[str] = set()
        for code, keywords in OKVED_KEYWORD_RULES.items():
            if any(kw in low for kw in keywords):
                okveds.add(code)
        # Также ищем явные коды ОКВЭД вида XX.XX в тексте
        for match in re.findall(r"\b\d{2}\.\d{2}\b", low):
            if match in OKVED_KEYWORD_RULES:
                okveds.add(match)
        return sorted(okveds)

    def extract_summary_facts(self, title: str, raw_text: str) -> List[str]:
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+", raw_text)
            if len(s.strip()) > 25
        ]
        # Приоритет предложениям с цифрами, процентами и финансовыми маркерами
        scored = sorted(
            sentences,
            key=lambda s: (
                bool(re.search(r"\d+%|\d+\s*(млрд|млн|дн|б\.п\.|руб)", s.lower())),
                len(s),
            ),
            reverse=True,
        )
        facts = scored[:2] if scored else [title]
        return facts

    def enrich_raw_item(self, raw: Dict[str, Any], idx: int = 0) -> NewsItem:
        title = self._clean_html(str(raw.get("title", "Без заголовка")))
        raw_text = self._clean_html(str(raw.get("raw_text") or raw.get("content") or title))
        combined = f"{title}. {raw_text}"

        macro_triggers = raw.get("macro_triggers") or self.extract_macro_triggers(combined)
        affected_okveds = raw.get("affected_okveds") or self.extract_affected_okveds(combined)
        summary_facts = raw.get("summary_facts") or self.extract_summary_facts(title, raw_text)
        tags = raw.get("tags") or sorted(set(macro_triggers + affected_okveds))

        news_id = str(
            raw.get("news_id")
            or f"NEWS_{idx:03d}_{hashlib.md5(title.encode('utf-8')).hexdigest()[:6]}"
        )

        return NewsItem(
            news_id=news_id,
            title=title,
            published_at=str(raw.get("published_at", "2026-08-31T12:00:00")),
            source_name=str(raw.get("source_name", "Деловые СМИ")),
            source_url=str(raw.get("source_url", "https://alfabank.ru")),
            raw_text=raw_text,
            summary_facts=summary_facts,
            tags=tags,
            affected_okveds=affected_okveds,
            macro_triggers=macro_triggers,
        )

    def load_from_json_or_csv(self, path: str | Path) -> List[NewsItem]:
        p = Path(path)
        if not p.exists():
            return []

        if p.suffix.lower() == ".json":
            with open(p, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
        else:
            df = pd.read_csv(p, encoding="utf-8")
            raw_list = df.to_dict(orient="records")

        items: List[NewsItem] = []
        seen_hashes: Set[str] = set()
        seen_tokens: List[Set[str]] = []

        for idx, raw in enumerate(raw_list, start=1):
            title = str(raw.get("title", ""))
            text = str(raw.get("raw_text") or raw.get("content") or "")
            if self._is_duplicate(title, text, seen_hashes, seen_tokens):
                continue
            items.append(self.enrich_raw_item(raw, idx=idx))

        return items

    def parse_rss_xml(self, xml_content: str, source_name: str = "RSS Feed") -> List[NewsItem]:
        """Парсит стандартную RSS-ленту без внешних зависимостей."""
        root = ET.fromstring(xml_content)
        raw_list: List[Dict[str, Any]] = []
        for item in root.findall(".//item"):
            raw_list.append(
                {
                    "title": item.findtext("title", default=""),
                    "raw_text": item.findtext("description", default=""),
                    "published_at": item.findtext("pubDate", default="2026-08-31"),
                    "source_name": source_name,
                    "source_url": item.findtext("link", default=""),
                }
            )
        return [self.enrich_raw_item(r, i) for i, r in enumerate(raw_list, start=1)]
