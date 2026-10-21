# src/services/context_builder.py
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

from src.models.schemas import CompanyContext, CounterpartyInfo, GroupContext
from src.services.synthetic_generator import SyntheticDataGenerator


PRODUCT_COLUMNS_MAP: Dict[str, str] = {
    "CL_PRODUCT_RKO_MARK": "РКО",
    "CL_PRODUCT_GAR_MARK": "Банковские гарантии",
    "CL_PRODUCT_LOA_MARK": "Кредитование",
    "CL_PRODUCT_LEA_MARK": "Лизинг",
    "CL_PRODUCT_DEP_MARK": "Депозиты",
    "CL_PRODUCT_ZPP_MARK": "Зарплатный проект",
    "FACTORING_MARK": "Факторинг",
}


class ClientContextBuilder:
    """Строит обогащенный бизнес-контекст клиента (CompanyContext)
    с устойчивой обработкой грязных/неполных CSV (Ограничение 05).
    """

    def __init__(
        self,
        uid_csv_path: str = "data/raw/df_Uid_data_hack.csv",
        fid_csv_path: str = "data/raw/df_Fid_Uid_link_hack.csv",
        auto_generate_if_missing: bool = True,
    ) -> None:
        self.uid_csv_path = Path(uid_csv_path)
        self.fid_csv_path = Path(fid_csv_path)

        if auto_generate_if_missing and (
            not self.uid_csv_path.exists() or not self.fid_csv_path.exists()
        ):
            SyntheticDataGenerator().generate_all(overwrite=False)

        self.df_uid = self._load_and_clean_uid(self.uid_csv_path)
        self.df_fid = self._load_and_clean_fid(self.fid_csv_path)
        self._uid_lookup: Dict[str, Dict[str, Any]] = {
            str(row["SYNTHETIC_U"]): row.to_dict()
            for _, row in self.df_uid.iterrows()
        }
        self._industry_stats = self._compute_industry_stats()
        self._group_stats = self._compute_group_stats()

    # -------------------- УСТОЙЧИВЫЕ ПАРСЕРЫ ГРЯЗНЫХ ДАННЫХ --------------------

    @staticmethod
    def _parse_bool_flag(val: Any) -> bool:
        if pd.isna(val) or val is None:
            return False
        if isinstance(val, (int, float)):
            return float(val) >= 1.0
        s = str(val).strip().lower()
        return s in {"1", "1.0", "true", "да", "yes", "y", "+"}

    @staticmethod
    def _parse_float(val: Any, default: float = 0.0) -> float:
        if pd.isna(val) or val is None:
            return default
        if isinstance(val, (int, float)):
            return float(val)
        cleaned = (
            str(val)
            .replace(" ", "")
            .replace("\u00a0", "")
            .replace(",", ".")
            .strip()
        )
        try:
            return float(cleaned)
        except ValueError:
            return default

    @staticmethod
    def _parse_int(val: Any, default: int = 0) -> int:
        return int(round(ClientContextBuilder._parse_float(val, float(default))))

    @staticmethod
    def _parse_str(val: Any, default: str = "Не указано") -> str:
        if pd.isna(val) or val is None:
            return default
        s = str(val).strip()
        if not s or s.lower() in {"nan", "none", "null", "н/д"}:
            return default
        return s

    @staticmethod
    def _parse_countries(val: Any) -> List[str]:
        if pd.isna(val) or val is None:
            return []
        raw = str(val).strip()
        if not raw or raw.lower() in {"nan", "none", "0", "нет"}:
            return []
        for sep in [";", "/", "|"]:
            raw = raw.replace(sep, ",")
        return [c.strip() for c in raw.split(",") if c.strip()]

    # -------------------- ЗАГРУЗКА И ПРЕДОБРАБОТКА CSV --------------------

    def _load_and_clean_uid(self, path: Path) -> pd.DataFrame:
        df = pd.read_csv(path, encoding="utf-8", low_memory=False)
        df["SYNTHETIC_U"] = df["SYNTHETIC_U"].apply(lambda x: self._parse_str(x, "UNKNOWN"))
        df["REVENUE_CLEAN"] = df.get("REVENUE_COMPANY", 0.0).apply(self._parse_float)
        df["OKVED_CLEAN"] = df.get("MAINOKVED_CODE", "").apply(
            lambda x: self._parse_str(x, "00.00")
        )
        df["OKVED_NAME_CLEAN"] = df.get("MAINOKVED_NAME", "").apply(
            lambda x: self._parse_str(x, "Отрасль не указана")
        )
        df["GROUP_CLEAN"] = df.get("GROUP_ID", "").apply(
            lambda x: self._parse_str(x, "")
        )
        return df

    def _load_and_clean_fid(self, path: Path) -> pd.DataFrame:
        df = pd.read_csv(path, encoding="utf-8", low_memory=False)
        for col in ["SYNTHETIC_F", "SYNTHETIC_U", "BENEFICIARY", "PAYER"]:
            if col not in df.columns:
                df[col] = None
        df["PAY_AMT_CLEAN"] = df.get("PAY_AMT", 0.0).apply(self._parse_float)
        df["PAY_CNT_CLEAN"] = df.get("PAY_CNT", 0).apply(self._parse_int)
        return df

    # -------------------- ОТРАСЛЕВАЯ АНАЛИТИКА И ХОЛДИНГИ --------------------

    def _compute_industry_stats(self) -> Dict[str, Dict[str, float]]:
        """Считает долю рынка в ОКВЭД и перцентиль по выручке."""
        stats: Dict[str, Dict[str, float]] = {}
        for okved, group in self.df_uid.groupby("OKVED_CLEAN"):
            total_rev = float(group["REVENUE_CLEAN"].sum())
            sorted_revs = group["REVENUE_CLEAN"].sort_values().tolist()
            n = len(sorted_revs)
            for _, row in group.iterrows():
                u_id = str(row["SYNTHETIC_U"])
                rev = float(row["REVENUE_CLEAN"])
                share_pct = round((rev / total_rev * 100.0), 2) if total_rev > 0 else 0.0
                if n <= 1:
                    # Если компания единственная в своем узком ОКВЭД в выборке — оцениваем перцентиль по всему датасету КБ
                    all_revs = self.df_uid["REVENUE_CLEAN"].sort_values().tolist()
                    rank_pos = sum(1 for r in all_revs if r <= rev)
                    percentile = round((rank_pos / max(len(all_revs), 1)) * 100.0, 1)
                else:
                    rank_pos = sum(1 for r in sorted_revs if r <= rev)
                    percentile = round((rank_pos / n) * 100.0, 1)
                stats[u_id] = {
                    "market_share_pct": share_pct,
                    "rank_percentile": percentile,
                }
        return stats

    def _compute_group_stats(self) -> Dict[str, GroupContext]:
        """Агрегирует метрики группы компаний (GROUP_ID)."""
        groups: Dict[str, GroupContext] = {}
        for _, row in self.df_uid.iterrows():
            u_id = str(row["SYNTHETIC_U"])
            grp_id = str(row["GROUP_CLEAN"])
            if not grp_id or grp_id == "Не указано":
                okved_label = f"{row['OKVED_CLEAN']} ({row['OKVED_NAME_CLEAN']})"
                groups[u_id] = GroupContext(
                    group_id=f"STANDALONE_{u_id}",
                    companies_count=1,
                    total_group_revenue=float(row["REVENUE_CLEAN"]),
                    group_okveds=[okved_label],
                )

        valid_groups = self.df_uid[self.df_uid["GROUP_CLEAN"] != ""]
        for grp_id, grp_df in valid_groups.groupby("GROUP_CLEAN"):
            cnt = len(grp_df)
            total_rev = float(grp_df["REVENUE_CLEAN"].sum())
            okveds = sorted(
                {
                    f"{r['OKVED_CLEAN']} ({r['OKVED_NAME_CLEAN']})"
                    for _, r in grp_df.iterrows()
                }
            )
            ctx = GroupContext(
                group_id=str(grp_id),
                companies_count=cnt,
                total_group_revenue=total_rev,
                group_okveds=okveds,
            )
            for u_id in grp_df["SYNTHETIC_U"]:
                groups[str(u_id)] = ctx
        return groups

    # -------------------- ГРАФ ПЛАТЕЖЕЙ И КОНТРАГЕНТОВ --------------------

    def _build_top_counterparties(
        self, synthetic_u: str, top_n: int = 3
    ) -> List[CounterpartyInfo]:
        result: List[CounterpartyInfo] = []
        payments_df = self.df_fid[self.df_fid["PAY_AMT_CLEAN"] > 0]

        # 1. Топ поставщиков (role = "supplier"): клиент (PAYER) платит контрагенту (BENEFICIARY)
        outgoing = payments_df[
            (payments_df["PAYER"].astype(str) == synthetic_u)
            & (payments_df["BENEFICIARY"].notna())
            & (payments_df["BENEFICIARY"].astype(str) != synthetic_u)
        ]
        total_out = float(outgoing["PAY_AMT_CLEAN"].sum())
        if total_out > 0:
            grouped_sup = (
                outgoing.groupby("BENEFICIARY", as_index=False)
                .agg({"PAY_AMT_CLEAN": "sum", "PAY_CNT_CLEAN": "sum"})
                .sort_values("PAY_AMT_CLEAN", ascending=False)
                .head(top_n)
            )
            for _, r in grouped_sup.iterrows():
                cp_id = str(r["BENEFICIARY"])
                cp_meta = self._uid_lookup.get(cp_id, {})
                amt = float(r["PAY_AMT_CLEAN"])
                cnt = int(r["PAY_CNT_CLEAN"])
                result.append(
                    CounterpartyInfo(
                        synthetic_u=cp_id,
                        role="supplier",
                        okved_code=self._parse_str(cp_meta.get("OKVED_CLEAN"), "00.00"),
                        okved_name=self._parse_str(
                            cp_meta.get("OKVED_NAME_CLEAN"), "Внешний контрагент"
                        ),
                        region=self._parse_str(cp_meta.get("REGION"), "Не указано"),
                        total_payment_amt=amt,
                        payment_cnt=cnt,
                        share_in_turnover_pct=round(amt / total_out * 100.0, 2),
                    )
                )

        # 2. Топ покупателей (role = "buyer"): контрагент (PAYER) платит клиенту (BENEFICIARY)
        incoming = payments_df[
            (payments_df["BENEFICIARY"].astype(str) == synthetic_u)
            & (payments_df["PAYER"].notna())
            & (payments_df["PAYER"].astype(str) != synthetic_u)
        ]
        total_in = float(incoming["PAY_AMT_CLEAN"].sum())
        if total_in > 0:
            grouped_buy = (
                incoming.groupby("PAYER", as_index=False)
                .agg({"PAY_AMT_CLEAN": "sum", "PAY_CNT_CLEAN": "sum"})
                .sort_values("PAY_AMT_CLEAN", ascending=False)
                .head(top_n)
            )
            for _, r in grouped_buy.iterrows():
                cp_id = str(r["PAYER"])
                cp_meta = self._uid_lookup.get(cp_id, {})
                amt = float(r["PAY_AMT_CLEAN"])
                cnt = int(r["PAY_CNT_CLEAN"])
                result.append(
                    CounterpartyInfo(
                        synthetic_u=cp_id,
                        role="buyer",
                        okved_code=self._parse_str(cp_meta.get("OKVED_CLEAN"), "00.00"),
                        okved_name=self._parse_str(
                            cp_meta.get("OKVED_NAME_CLEAN"), "Внешний покупатель"
                        ),
                        region=self._parse_str(cp_meta.get("REGION"), "Не указано"),
                        total_payment_amt=amt,
                        payment_cnt=cnt,
                        share_in_turnover_pct=round(amt / total_in * 100.0, 2),
                    )
                )

        return result

    # -------------------- ЯВНЫЕ ТРИГГЕРЫ ЧУВСТВИТЕЛЬНОСТИ --------------------

    def _build_risk_sensitivity_factors(
        self,
        row: Dict[str, Any],
        active_products: List[str],
        is_foreign_trade: bool,
        fts_countries: List[str],
        top_counterparties: List[CounterpartyInfo],
        workers_fns: str,
    ) -> List[str]:
        factors: List[str] = []
        okved = str(row.get("OKVED_CLEAN", ""))

        # 1. Процентный риск и долговая нагрузка vs Депозиты
        if "Кредитование" in active_products or "Лизинг" in active_products:
            factors.append(
                "Заемщик (Кредитование/Лизинг): высокая чувствительность к ключевой ставке ЦБ РФ (14,0%) и удорожанию рефинансирования"
            )
        if "Депозиты" in active_products and "Кредитование" not in active_products:
            factors.append(
                "Кэш-профиль (Депозиты без кредитной нагрузки): бенефициар жесткой ДКП ЦБ (14,0%) и высоких ставок размещения ликвидности"
            )

        # 2. ВЭД и валютно-таможенные риски
        if is_foreign_trade:
            countries_str = ", ".join(fts_countries) if fts_countries else "экспорт/импорт"
            factors.append(
                f"Участник ВЭД ({countries_str}): чувствительность к валютному курсу, срокам трансграничных платежей и таможенным пошлинам"
            )

        # 3. Рынок труда и ФОТ
        if any(tok in workers_fns for tok in ["1000", "5000", "10000", "Более"]):
            factors.append(
                f"Крупный работодатель ({workers_fns} сотр.): чувствительность к дефициту кадров и росту ФОТ (+8,5% г/г)"
            )

        # 4. Отраслевые макро-триггеры
        if okved.startswith("24.4"):
            factors.append(
                "Сырьевой экспортер (Драгметаллы/Золото): прямая зависимость денежного потока от мировых котировок золота"
            )
        elif okved.startswith("47."):
            factors.append(
                "Сектор розничной торговли: чувствительность к охлаждению потребительского спроса и переходу населения к сберегательной модели"
            )
        elif okved.startswith("49."):
            factors.append(
                "Транспорт и логистика: чувствительность к инфляции издержек, лизинговым ставкам и загрузке погранпереходов"
            )
        elif okved.startswith("41."):
            factors.append(
                "Строительный сектор: чувствительность к замедлению инвестиционного спроса (1П26), ставкам проектного финансирования и рискам подрядчиков"
            )
        elif okved.startswith("10."):
            factors.append(
                "Агропромышленный комплекс: чувствительность к экспортным квотам, портовым тарифам и отсрочкам платежей со стороны торговых сетей"
            )

        # 5. Негативные маркеры
        if self._parse_bool_flag(row.get("NEGATIVEMARK")):
            factors.append(
                "Комплаенс-триггер (NEGATIVEMARK=1): наличие негативных меток требует контроля ковенантов и рисков контрагентов"
            )

        # 6. Риск цепочки поставок (зависимость от ключевых поставщиков и покупателей)
        for cp in top_counterparties:
            if cp.share_in_turnover_pct >= 25.0:
                role_label = "поставщика" if cp.role == "supplier" else "покупателя"
                factors.append(
                    f"Концентрация цепочки поставок: зависимость от {role_label} {cp.synthetic_u} "
                    f"(ОКВЭД {cp.okved_code} — {cp.okved_name}, доля {cp.share_in_turnover_pct}%)"
                )

        return factors

    # -------------------- ПУБЛИЧНЫЕ МЕТОДЫ --------------------

    def list_company_ids(self) -> List[str]:
        return list(self._uid_lookup.keys())

    def build_context(self, synthetic_u: str) -> CompanyContext:
        if synthetic_u not in self._uid_lookup:
            raise KeyError(f"Компания {synthetic_u} не найдена в базе данных.")

        row = self._uid_lookup[synthetic_u]
        revenue = float(row["REVENUE_CLEAN"])
        ind = self._industry_stats.get(
            synthetic_u, {"market_share_pct": 0.0, "rank_percentile": 50.0}
        )
        percentile = ind["rank_percentile"]
        if percentile >= 80.0:
            pos_label = "Лидер отрасли (Топ-20%)"
        elif percentile >= 50.0:
            pos_label = "Крупный игрок выше медианы"
        else:
            pos_label = "Устойчивый игрок крупного бизнеса"

        # Банковские продукты (активные vs потенциал апсейла)
        active_products: List[str] = []
        available_upsell: List[str] = []
        for col, prod_name in PRODUCT_COLUMNS_MAP.items():
            if self._parse_bool_flag(row.get(col)):
                active_products.append(prod_name)
            else:
                available_upsell.append(prod_name)

        # ВЭД
        fts_countries = self._parse_countries(row.get("FTS_COUNTRY_NAME"))
        is_foreign_trade = self._parse_bool_flag(row.get("FTS_FLAG")) or bool(fts_countries)

        # Количество связанных физлиц
        f_links = self.df_fid[
            (self.df_fid["SYNTHETIC_U"].astype(str) == synthetic_u)
            & (self.df_fid["SYNTHETIC_F"].notna())
        ]
        linked_individuals_count = int(f_links["SYNTHETIC_F"].nunique())

        # Контрагенты и риски
        top_counterparties = self._build_top_counterparties(synthetic_u, top_n=3)
        workers_fns = self._parse_str(row.get("AMOUNT_WORKERS_FNS_GRADATION"))
        workers_spark = self._parse_str(
            row.get("AMOUNT_WORKERS_SPARK_GRADATION"), default=workers_fns
        )

        risk_factors = self._build_risk_sensitivity_factors(
            row=row,
            active_products=active_products,
            is_foreign_trade=is_foreign_trade,
            fts_countries=fts_countries,
            top_counterparties=top_counterparties,
            workers_fns=workers_fns,
        )

        return CompanyContext(
            synthetic_u=synthetic_u,
            org_type=self._parse_str(row.get("ORG_TYPE")),
            okfs_name=self._parse_str(row.get("OKFS_NAME")),
            company_age=self._parse_str(row.get("COMPANY_AGE_YEARS_GRADATION")),
            eco_stage=self._parse_str(row.get("ECO_MARK_LABEL")),
            main_okved_code=str(row["OKVED_CLEAN"]),
            main_okved_name=str(row["OKVED_NAME_CLEAN"]),
            revenue=revenue,
            industry_market_share_pct=ind["market_share_pct"],
            industry_rank_percentile=percentile,
            market_position_label=pos_label,
            city=self._parse_str(row.get("CITY")),
            region=self._parse_str(row.get("REGION")),
            workers_fns=workers_fns,
            workers_spark=workers_spark,
            is_foreign_trade=is_foreign_trade,
            fts_countries=fts_countries,
            active_products=active_products,
            available_upsell_products=available_upsell,
            risk_sensitivity_factors=risk_factors,
            group_context=self._group_stats[synthetic_u],
            top_counterparties=top_counterparties,
            linked_individuals_count=linked_individuals_count,
        )
