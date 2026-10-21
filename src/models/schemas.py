# src/models/schemas.py
from typing import List, Literal
from pydantic import BaseModel, Field


class CounterpartyInfo(BaseModel):
    synthetic_u: str
    role: Literal["supplier", "buyer"]
    okved_code: str
    okved_name: str
    region: str
    total_payment_amt: float
    payment_cnt: int
    share_in_turnover_pct: float


class GroupContext(BaseModel):
    group_id: str
    companies_count: int
    total_group_revenue: float
    group_okveds: List[str] = Field(default_factory=list)


class CompanyContext(BaseModel):
    synthetic_u: str
    org_type: str
    okfs_name: str
    company_age: str
    eco_stage: str
    main_okved_code: str
    main_okved_name: str
    revenue: float
    industry_market_share_pct: float
    industry_rank_percentile: float
    market_position_label: str
    city: str
    region: str
    workers_fns: str
    workers_spark: str
    is_foreign_trade: bool
    fts_countries: List[str] = Field(default_factory=list)
    active_products: List[str] = Field(default_factory=list)
    available_upsell_products: List[str] = Field(default_factory=list)
    risk_sensitivity_factors: List[str] = Field(default_factory=list)
    group_context: GroupContext
    top_counterparties: List[CounterpartyInfo] = Field(default_factory=list)
    linked_individuals_count: int


class NewsItem(BaseModel):
    news_id: str
    title: str
    published_at: str
    source_name: str
    source_url: str
    raw_text: str
    summary_facts: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    affected_okveds: List[str] = Field(default_factory=list)
    macro_triggers: List[str] = Field(default_factory=list)


class BankResearchChunk(BaseModel):
    chunk_id: str
    report_title: str
    topic: str
    content: str
    key_thesis: str
    published_date: str
