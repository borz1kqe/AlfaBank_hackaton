# -*- coding: utf-8 -*-
from typing import Dict, List
from pydantic import BaseModel

class CompanyProfile(BaseModel):
    synthetic_u: str
    name: str
    inn: str
    mainokved_code: str
    mainokved_name: str
    revenue_company: float
    credit_loa_mark: int
    fts_country_name: str
    key_counterparties: List[str]

    # Совместимость с любыми обращениями
    @property
    def annual_revenue_mln(self) -> float:
        return self.revenue_company

    @property
    def credit_portfolio_mln(self) -> float:
        return 3200.0 if self.synthetic_u == "U_AGRO_98231" else 1500.0

    @property
    def id(self) -> str:
        return self.synthetic_u

    @property
    def okved(self) -> str:
        return f"{self.mainokved_code} ({self.mainokved_name})"

    @property
    def fx_exposure(self) -> str:
        return self.fts_country_name


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
        synthetic_u="U_AGRO_98231",
        name="ПАО «АгроПром Холдинг»",
        inn="7705912345",
        mainokved_code="01.11",
        mainokved_name="Выращивание зерновых культур",
        revenue_company=18400.0,
        credit_loa_mark=1,
        fts_country_name="Китай, Турция, ОАЭ",
        key_counterparties=["ООО «ЮгЗерноТрейд»", "АО «Морской Порт»", "ООО «АгроХимСнаб»"]
    ),
    CompanyProfile(
        synthetic_u="U_TECH_45109",
        name="АО «Объединенные Микросистемы»",
        inn="7723847561",
        mainokved_code="26.11",
        mainokved_name="Производство электронных компонентов",
        revenue_company=16200.0,
        credit_loa_mark=1,
        fts_country_name="Китай",
        key_counterparties=["Shenzhen Tech Ltd", "ООО «ПромИнжиниринг»", "АО «РостехКомплект»"]
    )
]

MOCK_INSIGHTS = [
    PersonalizedInsight(
        id="ins_cbr_14_rate",
        company_id="U_AGRO_98231",
        target_roles=["CEO", "CFO", "TREASURER", "ACCOUNTANT"],
        title="Совет директоров Банка России сохранил ключевую ставку на уровне 14,0% годовых",
        urgency="CRITICAL",
        publish_date="11 сентября 2026, 13:30",
        source_name="Пресс-служба Банка России",
        source_url="https://cbr.ru",
        fact_summary="11 сентября 2026 года ЦБ РФ сохранил ключевую ставку на уровне 14% годовых. Это первая пауза в цикле смягчения денежно-кредитной политики, начавшемся в июне 2025 года. Сигнал регулятора ужесточен.",
        triggers=[
            "MAINOKVED: 01.11 (Высокая зависимость от сезонных оборотных кредитов)",
            "CL_PRODUCT_LOA_MARK: 1 (Кредитный портфель 3.2 млрд ₽, плавающая ставка КС+2.2%)",
            "FTS_COUNTRY_NAME: Китай, ОАЭ (Экспортная выручка в CNY и AED)",
            "REVENUE_COMPANY: 18.4 млрд ₽ (Крупный бизнес, Слайд 4)"
        ],
        counterparty_impact="Покупатель ООО «ЮгЗерноТрейд» запросил отсрочку расчетов на 30 дней в связи с паузой удешевления овердрафтов.",
        risks=[
            "Финансовая нагрузка по обслуживанию долга не снизится (процентные расходы: 38.5 млн ₽/мес).",
            "Риск нарушения ковенанты Чистый Долг / EBITDA (> 2.8x при удержании текущих ставок).",
            "Удорожание факторингового финансирования для покупателей зерна."
        ],
        opportunities=[
            "Размещение операционной ликвидности в овернайт-депозиты Альфа-Банка под 13.8% годовых.",
            "Фиксация ставки на текущем дне цикла через процентные свопы (IRS) Альфа-Банка."
        ],
        alfa_view=AlfaMacroView(
            analyst_quote="Для бизнеса сохранение ставки на уровне 14% — четкий сигнал: период быстрого удешевления кредитов приостановлен. Деньги остаются дорогими, нагрузка на компании с долгом не снизится в 2П26.",
            report_title="Ключевая ставка ЦБ РФ: ставка без изменения на 14,0%, риторика стала жестче",
            report_date="Сентябрь 2026",
            alfa_base_forecast="Базовый сценарий Альфа-Банка: КС 14.0% до конца 2026 г., средняя ставка на 2027 г. — 12.5%."
        ),
        ai_inference=AIInference(
            custom_forecast="Для ПАО «АгроПром Холдинг» сохранение ставки 14% означает отсутствие ожидаемой экономии 24 млн ₽ на процентах в 4 кв. 2026 г.",
            confidence_score=0.96,
            primary_driver="Доля плавающего долга 2.08 млрд ₽ при фиксации жесткой ДКП"
        ),
        recommended_actions={
            "CEO": [
                "Скорректировать инвестиционный бюджет 2026–2027 гг. с учетом отсутствия удешевления заемного капитала.",
                "Провести переговоры с трейдерами по переходу на аккредитивную форму расчетов."
            ],
            "CFO": [
                "Заключить соглашение IRS (процентный своп) с Альфа-Банком по траншу 1.5 млрд ₽ для фиксации эффективной ставки 12.8%.",
                "Провести стресс-тест ликвидности при удержании ставки 14% до середины 2027 года."
            ],
            "TREASURER": [
                "Перевести свободный остаток 450 млн ₽ в неснижаемый остаток (НСО) Альфа-Бизнес под 13.85%.",
                "Оптимизировать внутригрупповые займы для минимизации внешнего овердрафта."
            ],
            "ACCOUNTANT": [
                "Скорректировать график дисконтирования арендных и кредитных обязательств по ФСБУ 25/2018.",
                "Создать резерв по сомнительной дебиторской задолженности покупателей зерна."
            ]
        },
        banking_product=BankingProductOffer(
            product_name="Хеджирование процентных рисков (IRS Альфа-Банк)",
            badge="Рекомендовано CFO",
            description="Зафиксируйте ставку по кредитам с плавающей ставкой на уровне 12.8% на срок до 24 месяцев.",
            cta_text="Рассчитать параметры свопа"
        ),
        traceability=[
            TraceabilityStep(stage="1. Регуляторный триггер", detail="Пресс-релиз ЦБ РФ от 11.09.2026 (Сохранение КС на 14.0%).", source="cbr.ru/press/pr"),
            TraceabilityStep(stage="2. Сопоставление с df_Uid_data_hack.csv", detail="Клиент SYNTHETIC_U: U_AGRO_98231, CL_PRODUCT_LOA_MARK=1, REVENUE=18.4 млрд ₽.", source="df_Uid_data_hack.csv"),
            TraceabilityStep(stage="3. Аналитика Центра макроэкономических исследований", detail="Отчет: «Ключевая ставка ЦБ РФ: ставка без изменения на 14,0%, риторика стала жестче».", source="Alfa Macro Research (Слайд 17)"),
            TraceabilityStep(stage="4. Валидация Guardrail & Qwen3.6 35B", detail="Сформирован персонализированный чек-лист действий под 4 роли ЛПР. Факт-чекинг пройден.", source="Guardrail Engine")
        ]
    )
]

CHAT_RESPONSES = {
    "долговую нагрузку": (
        "📊 **Расчет влияния на долговую нагрузку (CFO View):**\n\n"
        "• Сохранение ставки на уровне 14,0% замораживает ежемесячные процентные расходы на уровне **38.5 млн ₽**.\n"
        "• Ожидавшееся снижение ставки на 100 б.п. принесло бы экономию в **2.1 млн ₽/мес** — этот эффект откладывается минимум на 2 квартала.\n"
        "• Коэффициент покрытия процентов (ICR) составит 3.4x при допустимом ковенантном минимуме 2.5x.\n"
        "• **Рекомендация:** перевести 1.5 млрд ₽ кредитного портфеля в фиксированную ставку через IRS Альфа-Банка."
    ),
    "поставщиках": (
        "🚚 **Влияние на цепочку контрагентов (df_Uid_payment_hack.csv):**\n\n"
        "• Ключевой покупатель **ООО «ЮгЗерноТрейд»** (объем платежей 1.2 млрд ₽) запросил пролонгацию отсрочки до 45 дней.\n"
        "• **Рекомендация:** подключить агентский факторинг от Альфа-Банка — банк оплатит до 90% поставки в день отгрузки."
    ),
    "default": (
        "🤖 **Аналитический ассистент Альфа-Инсайт:**\n\n"
        "На основе сопоставления профиля компании и макро-отчета Альфа-Банка, удержание жесткой риторики требует оптимизации структуры рабочего капитала. Рекомендуем запросить встречу с корпоративным банкиром Альфа-Банка."
    )
}
