# src/models/schemas.py
from typing import List, Literal, Optional
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
    group_id: Optional[str] = "GRP_DEFAULT"
    companies_count: int = 1
    total_group_revenue: float = 0.0
    group_okveds: List[str] = Field(default_factory=list)


class CompanyContext(BaseModel):
    synthetic_u: str
    display_name: Optional[str] = None
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
    published_date: str = "Сентябрь 2026"


# --- СХЕМЫ ВЫВОДА AI-АГЕНТА И ИНТЕРАКТИВНОГО ЧАТА (Роль 2) ---

class WhatHappenedBlock(BaseModel):
    title: str
    facts: List[str] = Field(default_factory=list)
    source_name: str
    source_url: str
    published_at: str


class WhyImportantBlock(BaseModel):
    summary: str
    matched_company_features: List[str] = Field(default_factory=list)
    supply_chain_impact: Optional[str] = None


class ConsequencesBlock(BaseModel):
    risks: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    horizon: str = "Краткосрочный и среднесрочный (1–6 мес.)"


class BankEvaluationBlock(BaseModel):
    alfa_bank_position: str
    cited_report_title: str
    ai_model_inference: str


class NativeProductOffer(BaseModel):
    product_name: str
    pitch: str
    cta_label: str = "Оставить заявку в Альфа-Бизнес"


class RecommendedActionsBlock(BaseModel):
    steps_for_role: List[str] = Field(default_factory=list)
    native_bank_product: NativeProductOffer


class AgentTraceStep(BaseModel):
    step_name: str
    tool_used: str
    reasoning: str
    status: str = "completed"


class TraceabilityBlock(BaseModel):
    used_sources: List[str] = Field(default_factory=list)
    company_triggers_used: List[str] = Field(default_factory=list)
    llm_models_used: List[str] = Field(default_factory=list)
    agent_steps: List[AgentTraceStep] = Field(default_factory=list)


class PersonalizedInsight(BaseModel):
    insight_id: str
    news_id: str
    company_id: str
    target_role: str
    relevance_score: int = Field(ge=0, le=100)
    urgency_badge: Literal["Критично", "Важно", "Обзорно"]

    what_happened: WhatHappenedBlock
    why_important_for_company: WhyImportantBlock
    consequences: ConsequencesBlock
    bank_evaluation: BankEvaluationBlock
    recommended_actions: RecommendedActionsBlock
    traceability: TraceabilityBlock


class ChatRequest(BaseModel):
    company_id: str
    role: str = "CFO"
    insight_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    cited_sources: List[str] = Field(default_factory=list)
    model_used: str
    follow_up_suggestions: List[str] = Field(default_factory=list)
