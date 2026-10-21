# -*- coding: utf-8 -*-
from typing import Dict, List
from pydantic import BaseModel

class CompanyProfile(BaseModel):
    id: str
    name: str
    inn: str
    okved: str
    industry: str
    annual_revenue_mln: float
    credit_portfolio_mln: float
    fx_exposure: str
    key_counterparties: List[str]

class AlfaMacroView(BaseModel):
    analyst_quote: str
    report_title: str
    report_date: str
    alfa_base_forecast: str

class AIInference(BaseModel):
    custom_forecast: str
    confidence_score: float
    primary_driver: str

class BankingProductOffer(BaseModel):
    product_name: str
    badge: str
    description: str
    cta_text: str
    cta_action: str

class TraceabilityStep(BaseModel):
    stage: str
    detail: str
    source: str

class PersonalizedInsight(BaseModel):
    id: str
    company_id: str
    target_roles: List[str]
    title: str
    urgency: str
    publish_date: str
    source_name: str
    source_url: str
    fact_summary: str
    triggers: List[str]
    counterparty_impact: str
    risks: List[str]
    opportunities: List[str]
    alfa_view: AlfaMacroView
    ai_inference: AIInference
    recommended_actions: Dict[str, List[str]]
    banking_product: BankingProductOffer
    traceability: List[TraceabilityStep]

MOCK_COMPANIES = [
    CompanyProfile(
        id="comp_agro_01",
        name="ООО «АгроХолдинг Волга»",
        inn="7705123456",
        okved="01.11 (Выращивание зерновых)",
        industry="Агропромышленный комплекс",
        annual_revenue_mln=4200.0,
        credit_portfolio_mln=850.0,
        fx_exposure="Экспортная выручка (CNY, AED), закупки удобрений (RUB)",
        key_counterparties=["ПАО ТД Зернотрейд", "ООО ХимЭкспорт", "АО Порт Новороссийск"]
    ),
    CompanyProfile(
        id="comp_tech_02",
        name="АО «Микроэлектроника Инжиниринг»",
        inn="7723987654",
        okved="26.11 (Производство электронных компонентов)",
        industry="Высокие технологии и приборостроение",
        annual_revenue_mln=1850.0,
        credit_portfolio_mln=320.0,
        fx_exposure="Импорт сырья из ЮВА (USD, CNY 80%)",
        key_counterparties=["Shenzhen Tech Ltd", "ООО ПромСнаб", "АО РостехКомпонент"]
    )
]

MOCK_INSIGHTS = [
    PersonalizedInsight(
        id="ins_cbr_rate_01",
        company_id="comp_agro_01",
        target_roles=["CEO", "CFO", "TREASURER", "ACCOUNTANT"],
        title="ЦБ РФ повысил ключевую ставку до 21%: рост стоимости флоатеров",
        urgency="CRITICAL",
        publish_date="Сегодня, 13:30",
        source_name="Банк России",
        source_url="https://cbr.ru",
        fact_summary="Совет директоров Банка России поднял ключевую ставку до 21,00% годовых.",
        triggers=[
            "ОКВЭД 01.11 (Высокая зависимость от оборотных кредитов)",
            "Кредитный портфель: 850 млн ₽ (72% с плавающей ставкой КС+2.8%)",
            "Ежемесячный платеж вырастет на 1.41 млн ₽"
        ],
        counterparty_impact="Риск кассового разрыва: покупатели зерна просят отсрочку 45 дней.",
        risks=[
            "Рост годовых процентных расходов компании на 17.0 млн ₽.",
            "Нарушение ковенанты Net Debt / EBITDA (> 3.2x)."
        ],
        opportunities=[
            "Размещение остатков на овернайт-депозитах Альфа-Банка под 20.8%."
        ],
        alfa_view=AlfaMacroView(
            analyst_quote="Ожидаем удержания ставки на уровне 20–21% до середины 2025 г.",
            report_title="Макрообзор Альфа-Банка: Стратегия высоких ставок",
            report_date="Октябрь 2024",
            alfa_base_forecast="КС на конец года: 21.0%."
        ),
        ai_inference=AIInference(
            custom_forecast="Критический порог ликвидности наступит через 48 дней без фиксации ставки.",
            confidence_score=0.94,
            primary_driver="Доля плавающего долга 850 млн ₽"
        ),
        recommended_actions={
            "CEO": ["Заморозить некапитальные стройки на 2025 год."],
            "CFO": ["Зафиксировать ставку через IRS-своп Альфа-Банка по траншу 450 млн ₽."],
            "TREASURER": ["Перевести остатки 120 млн ₽ в неснижаемый остаток (НСО) под 20.85%."],
            "ACCOUNTANT": ["Сформировать резерв по сомнительным долгам дебиторов."]
        },
        banking_product=BankingProductOffer(
            product_name="Процентный своп (IRS Альфа-Банк)",
            badge="Рекомендовано CFO",
            description="Зафиксируйте ставку на уровне 18.2% на 18 месяцев.",
            cta_text="Рассчитать хедж",
            cta_action="open_irs"
        ),
        traceability=[
            TraceabilityStep(stage="1. Релиз ЦБ", detail="Релиз ставки +200 bps", source="cbr.ru"),
            TraceabilityStep(stage="2. ERP Match", detail="Кредит №448-КЛ (КС+2.8%)", source="Core API"),
            TraceabilityStep(stage="3. Guardrail", detail="Проверка гипотез пройдена", source="AI Guardrail")
        ]
    )
]

CHAT_RESPONSES = {
    "default": "Анализ Альфа-Инсайт: событие увеличивает процентные расходы на 1.41 млн ₽/мес. Рекомендуется зафиксировать ставку через IRS."
}
