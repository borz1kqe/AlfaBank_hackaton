# src/api/main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from src.models.schemas import (
    CompanyContext,
    CounterpartyInfo,
    GroupContext,
    NewsItem,
    BankResearchChunk,
    PersonalizedInsight,
    ChatRequest,
    ChatResponse,
)
from src.services.llm_client import SafeLLMClient
from src.services.agent import BusinessInsightAgent, ROLE_PERSONAS

app = FastAPI(
    title="Alfa-Business AI News Analytics API",
    description="Многошаговый AI-сервис персонализированной новостной аналитики для крупного бизнеса Альфа-Банка",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_client = SafeLLMClient()
agent = BusinessInsightAgent(llm_client=llm_client)

# Автоподключение RAGStore от Участника 1 (если присутствует)
rag_store_instance = None
try:
    from src.services.rag_store import RAGStore
    rag_store_instance = RAGStore()
except Exception:
    rag_store_instance = None

COMPANIES_DB: Dict[str, CompanyContext] = {
    "U_1001": CompanyContext(
        synthetic_u="U_1001",
        display_name="ПАО «УралМеталлЭкспорт» (SYNTHETIC_U: U_1001)",
        org_type="Корпорация",
        okfs_name="Частная собственность",
        company_age="Более 15 лет",
        eco_stage="Зрелый бизнес",
        main_okved_code="24.10",
        main_okved_name="Производство чугуна, стали и ферросплавов",
        revenue=68_500_000_000.0,
        industry_market_share_pct=14.8,
        industry_rank_percentile=94.5,
        market_position_label="Лидер отрасли (Топ-10%)",
        city="Екатеринбург",
        region="Свердловская область",
        workers_fns="5000+",
        workers_spark="5000+",
        is_foreign_trade=True,
        fts_countries=["Китай", "Турция", "ОАЭ"],
        active_products=["РКО (Расчетно-кассовое обслуживание)", "Кредитование", "Зарплатный проект", "Банковские гарантии"],
        available_upsell_products=["Факторинг", "Валютное хеджирование", "Депозиты / Размещение ликвидности"],
        risk_sensitivity_factors=[
            "Заемщик (CL_PRODUCT_LOA_MARK=1): высокая чувствительность к ключевой ставке ЦБ (14%) и стоимости обслуживания долга.",
            "Экспортер/Участник ВЭД (FTS_FLAG=1, Китай/Турция): чувствительность к ценам на металлы (Commodities) и валютным курсам.",
            "Холдинговая структура (GROUP_ID=GRP_01): 4 связанные компании с совокупной выручкой 92 млрд руб.",
        ],
        group_context=GroupContext(
            group_id="GRP_01",
            companies_count=4,
            total_group_revenue=92_000_000_000.0,
            group_okveds=["Производство чугуна, стали и ферросплавов", "Добыча железных руд", "Грузовые ж/д перевозки"],
        ),
        top_counterparties=[
            CounterpartyInfo(
                synthetic_u="U_2045",
                role="supplier",
                okved_code="49.20",
                okved_name="Деятельность железнодорожного транспорта: грузовые перевозки",
                region="г. Москва",
                total_payment_amt=8_400_000_000.0,
                payment_cnt=142,
                share_in_turnover_pct=34.5,
            ),
            CounterpartyInfo(
                synthetic_u="U_3012",
                role="buyer",
                okved_code="41.20",
                okved_name="Строительство жилых и нежилых зданий",
                region="г. Москва",
                total_payment_amt=12_100_000_000.0,
                payment_cnt=89,
                share_in_turnover_pct=41.2,
            ),
        ],
        linked_individuals_count=5,
    ),
    "U_1002": CompanyContext(
        synthetic_u="U_1002",
        display_name="АО «Федеральная Торговая Сеть Прайм» (SYNTHETIC_U: U_1002)",
        org_type="Крупный бизнес",
        okfs_name="Частная собственность",
        company_age="10–15 лет",
        eco_stage="Активный рост",
        main_okved_code="47.11",
        main_okved_name="Торговля розничная преимущественно пищевыми продуктами в неспециализированных магазинах",
        revenue=42_000_000_000.0,
        industry_market_share_pct=8.2,
        industry_rank_percentile=86.0,
        market_position_label="Крупный отраслевой игрок",
        city="Москва",
        region="г. Москва",
        workers_fns="10000+",
        workers_spark="10000+",
        is_foreign_trade=True,
        fts_countries=["Беларусь", "Казахстан"],
        active_products=["РКО (Расчетно-кассовое обслуживание)", "Кредитование", "Лизинг", "Депозиты / Размещение ликвидности", "Факторинг"],
        available_upsell_products=["Банковские гарантии", "Зарплатный проект"],
        risk_sensitivity_factors=[
            "Кредиты и Лизинг (CL_PRODUCT_LOA_MARK=1, LEA_MARK=1): чувствительность к ставке ЦБ при финансировании складов и автопарка.",
            "Массовый работодатель (10000+ сотрудников): критическая чувствительность к дефициту на рынке труда и росту ФОТ.",
            "Розничный сектор: прямая зависимость от потребительского спроса и недельной инфляции.",
        ],
        group_context=GroupContext(
            group_id="GRP_02",
            companies_count=2,
            total_group_revenue=49_500_000_000.0,
            group_okveds=["Торговля розничная", "Складское хозяйство и хранение"],
        ),
        top_counterparties=[
            CounterpartyInfo(
                synthetic_u="U_4088",
                role="supplier",
                okved_code="10.51",
                okved_name="Производство молока и молочной продукции",
                region="Московская область",
                total_payment_amt=5_200_000_000.0,
                payment_cnt=310,
                share_in_turnover_pct=28.0,
            ),
        ],
        linked_individuals_count=3,
    ),
}

BANK_RESEARCH_DB: List[BankResearchChunk] = [
    BankResearchChunk(
        chunk_id="alfa_01",
        report_title="Ключевая ставка ЦБ РФ: ставка без изменения на 14,0%, риторика стала жестче",
        topic="Денежно-кредитная политика, кредиты, ключевая ставка",
        content="11 сентября 2026 года совет директоров Банка России принял решение сохранить ключевую ставку на уровне 14,0% годовых. Это первая пауза в цикле смягчения ДКП после десяти последовательных снижений ставки, начавшегося в июне 2025 года.",
        key_thesis="Для бизнеса сохранение ключевой ставки на уровне 14% — сигнал о том, что период быстрого удешевления кредитов временно приостановлен. Деньги остаются дорогими, финансовая нагрузка на компании с заемным финансированием не снизится в ближайшей перспективе.",
        published_date="11 сентября 2026",
    ),
    BankResearchChunk(
        chunk_id="alfa_02",
        report_title="Макростатистика 7М26: данные по рынку труда не подтверждают охлаждения экономики",
        topic="Рынок труда, зарплаты, безработица, издержки бизнеса",
        content="По итогам 7 месяцев 2026 года безработица остается на историческом минимуме, а конкуренция за персонал в промышленности, логистике и ритейле продолжает разгонять зарплаты.",
        key_thesis="Дефицит кадров остается главным ограничением роста производства и проинфляционным фактором, требуя от трудоемкого бизнеса закладывать рост ФОТ на 12-15%.",
        published_date="Сентябрь 2026",
    ),
    BankResearchChunk(
        chunk_id="alfa_03",
        report_title="Commodities performance и Обзор рынка золота, август 2026",
        topic="Сырьевые рынки, металлы, золото, экспорт, ВЭД",
        content="В августе 2026 года котировки золота обновили максимумы, тогда как цены на черные и промышленные металлы испытывают давление из-за охлаждения строительного сектора в Азии и роста логистических тарифов.",
        key_thesis="Экспортерам черной металлургии следует готовиться к волатильности экспортной премии и контролировать транспортно-логистическое плечо при поставках в Китай и Турцию.",
        published_date="Август 2026",
    ),
]

NEWS_DB: List[NewsItem] = [
    NewsItem(
        news_id="news_101",
        title="Банк России сохранил ключевую ставку на уровне 14% годовых и ужесточил сигнал",
        published_at="11 сентября 2026, 13:30",
        source_name="Банк России / Интерфакс",
        source_url="https://cbr.ru/press/",
        raw_text="Совет директоров Банка России 11 сентября 2026 года принял решение сохранить ключевую ставку на уровне 14,00% годовых. Это первая пауза после десяти последовательных снижений ставки с июня 2025 года.",
        summary_facts=[
            "Ключевая ставка ЦБ РФ сохранена на уровне 14,0% годовых (решение от 11.09.2026).",
            "Прерван цикл из 10 подряд снижений ставки, длившийся с июня 2025 года.",
            "Регулятор дал жесткий сигнал о готовности удерживать высокую ставку до устойчивого замедления инфляции.",
        ],
        tags=["ДКП", "Ключевая ставка", "Кредиты", "Финансы"],
        affected_okveds=["24.10", "41.20", "47.11", "49.20"],
        macro_triggers=["key_rate", "ставка", "кредит", "bonds"],
    ),
    NewsItem(
        news_id="news_102",
        title="РЖД и операторы грузоперевозок индексируют тарифы на экспортные направления в Китай и порты Юга",
        published_at="12 сентября 2026, 10:15",
        source_name="Коммерсантъ",
        source_url="https://www.kommersant.ru/",
        raw_text="Крупнейшие железнодорожные операторы объявили о пересмотре ставок предоставления полувагонов и контейнеров на восточном и южном экспортных направлениях в 3–4 квартале 2026 года на 9–12%.",
        summary_facts=[
            "Ставки на грузовые ж/д перевозки в направлении Китая и южных портов вырастут на 9–12% в 3–4 кв. 2026 г.",
            "Причины: высокая стоимость лизинга подвижного состава и дефицит кадров в логистике.",
            "Наибольшее влияние ощутят экспортеры черных металлов, угля и удобрений.",
        ],
        tags=["Логистика", "ВЭД", "Экспорт", "Металлургия"],
        affected_okveds=["24.10", "49.20"],
        macro_triggers=["fx", "вэд", "commodities", "сырье", "логистика"],
    ),
    NewsItem(
        news_id="news_103",
        title="Дефицит линейного персонала в ритейле и складской логистике достиг максимума к осени 2026 года",
        published_at="12 сентября 2026, 11:40",
        source_name="РБК",
        source_url="https://www.rbc.ru/",
        raw_text="По данным отраслевого мониторинга за 7 месяцев 2026 года, нехватка складских работников, водителей и персонала торговых залов привела к ускорению роста предлагаемых зарплат на 16% год к году.",
        summary_facts=[
            "Зарплатные предложения для линейного персонала в ритейле и логистике выросли на 16% г/г.",
            "Охлаждения на рынке труда по итогам 7М26 не фиксируется.",
            "Одновременно фиксируется прохождение пика потребительского спроса.",
        ],
        tags=["Рынок труда", "Ритейл", "Инфляция", "Издержки"],
        affected_okveds=["47.11", "10.51", "52.10"],
        macro_triggers=["labor", "inflation", "gdp"],
    ),
]


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "alfa-ai-agent-backend"}


@app.get("/api/companies")
def list_companies():
    return {
        "companies": [
            {
                "synthetic_u": c.synthetic_u,
                "display_name": c.display_name or c.synthetic_u,
                "main_okved_code": c.main_okved_code,
                "main_okved_name": c.main_okved_name,
                "revenue": c.revenue,
                "market_position_label": c.market_position_label,
                "region": c.region,
            }
            for c in COMPANIES_DB.values()
        ],
        "roles": [
            {"code": code, "title": info["title"], "focus": info["focus"]}
            for code, info in ROLE_PERSONAS.items()
        ],
    }


@app.get("/api/companies/{company_id}/context", response_model=CompanyContext)
def get_company_context(company_id: str):
    if company_id in COMPANIES_DB:
        return COMPANIES_DB[company_id]
    if rag_store_instance and hasattr(rag_store_instance, "get_company_context"):
        try:
            return rag_store_instance.get_company_context(company_id)
        except Exception:
            pass
    raise HTTPException(status_code=404, detail=f"Компания {company_id} не найдена")


@app.get("/api/feed", response_model=List[PersonalizedInsight])
def get_personalized_feed(
    company_id: str = Query("U_1001", description="SYNTHETIC_U компании"),
    role: str = Query("CFO", description="Роль ЛПР: CEO, CFO, TREASURER, ACCOUNTANT"),
):
    company = get_company_context(company_id)
    return agent.generate_feed_for_client(
        company=company,
        role=role,
        news_list=NEWS_DB,
        bank_chunks=BANK_RESEARCH_DB,
    )


@app.post("/api/chat", response_model=ChatResponse)
def ask_followup_question(req: ChatRequest):
    company = get_company_context(req.company_id)
    feed = agent.generate_feed_for_client(company, req.role, NEWS_DB, BANK_RESEARCH_DB)
    target_insight = next((i for i in feed if i.insight_id == req.insight_id), feed[0])
    return agent.answer_followup_question(req, company, target_insight)
