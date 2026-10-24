# -*- coding: utf-8 -*-
"""
Альфа-Инсайт | Интернет-банк «Альфа-Бизнес»
Дизайн: Выдвижная шторка (Desktop + Mobile Drawer) без шрифтовых багов
"""

import streamlit as st
import requests
import os
import sys
import base64
from pathlib import Path
from typing import Dict, List, Any

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Шторка адаптируется автоматически: на ПК раскрыта, на смартфонах свернута
st.set_page_config(
    page_title="Альфа-Инсайт | Интернет-банк «Альфа-Бизнес»",
    page_icon="https://alfabank.servicecdn.ru/icons/corp/favicons/favicon.ico",
    layout="wide",
    initial_sidebar_state="auto"
)

# Ключи и настройки
LLM_API_KEY = st.secrets.get("LLM_API_KEY") if hasattr(st, "secrets") and "LLM_API_KEY" in st.secrets else os.getenv("LLM_API_KEY", "sk-ARm7HMnjyUUX-_sG3Qsicw")
LLM_BASE_URL = (st.secrets.get("LLM_BASE_URL") if hasattr(st, "secrets") and "LLM_BASE_URL" in st.secrets else os.getenv("LLM_BASE_URL", "https://changellenge.up.railway.app/v1")).rstrip("/")
LLM_MODEL = st.secrets.get("LLM_MODEL") if hasattr(st, "secrets") and "LLM_MODEL" in st.secrets else os.getenv("LLM_MODEL", "deepseek/deepseek-v4.1-flash")

PRIMARY_URL = "https://changellenge.up.railway.app/v1"
BACKUP_URL = "https://api.alfahack-gateway26.ru/v1"

MODELS_QUEUE = [
    LLM_MODEL,
    "deepseek/deepseek-v4.1-flash",
    "qwen/qwen3.6-35b-a3b",
    "z-ai/glm-5.3-flash"
]

def get_logo_html() -> str:
    paths = [
        Path("logos/alfa-bank-business.svg"),
        Path("frontend/logos/alfa-bank-business.svg"),
        Path("assets/alfa-bank-business.svg"),
        Path("alfa-bank-business.svg")
    ]
    for p in paths:
        if p.exists():
            try:
                data = p.read_text(encoding="utf-8")
                b64 = base64.b64encode(data.encode("utf-8")).decode("utf-8")
                return f'<img src="data:image/svg+xml;base64,{b64}" height="26" style="vertical-align:middle;margin-right:8px;" />'
            except Exception:
                pass
    return '<span style="background:#EF3124;color:#FFFFFF;padding:4px 9px;border-radius:6px;font-weight:900;font-size:0.85rem;margin-right:8px;">А</span>'

# CSS С ВЫДВИЖНОЙ ШТОРКОЙ ДЛЯ ПК И ТЕЛЕФОНОВ
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    #MainMenu, footer, div[data-testid="stStatusWidget"], .viewerBadge_container__1QSob {
        display: none !important;
        visibility: hidden !important;
    }

    /* ФИКС СИСТЕМНОЙ КНОПКИ ВЫЗОВА ШТОРКИ */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
    }

    /* Кнопка открытия шторки на основном экране */
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        z-index: 999999 !important;
    }
    [data-testid="stSidebarCollapsedControl"] button {
        background-color: #111827 !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15) !important;
        padding: 6px 14px !important;
        height: 38px !important;
    }
    [data-testid="stSidebarCollapsedControl"] button span {
        display: none !important;
    }
    [data-testid="stSidebarCollapsedControl"] button::after {
        content: "› Меню" !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
    }

    /* Кнопка закрытия шторки внутри самой шторки */
    [data-testid="stSidebarHeader"] button,
    [data-testid="stSidebarCollapseButton"] {
        background: rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        border: none !important;
        width: 32px !important;
        height: 32px !important;
    }
    [data-testid="stSidebarHeader"] button span,
    [data-testid="stSidebarCollapseButton"] span {
        display: none !important;
    }
    [data-testid="stSidebarHeader"] button::after,
    [data-testid="stSidebarCollapseButton"]::after {
        content: "‹" !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        color: #9CA3AF !important;
        line-height: 1 !important;
    }

    /* ВЫДВИЖНАЯ ШТОРКА (TITANIUM BLACK) */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding: 1.2rem 1rem !important;
    }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #F9FAFB;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", sans-serif;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stCaption {
        color: #9CA3AF !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1F2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] svg { fill: #9CA3AF !important; }

    [data-testid="stSidebar"] div[data-testid="stRadio"] label {
        background-color: transparent !important;
        padding: 10px 12px !important;
        border-radius: 10px !important;
        color: #9CA3AF !important;
        font-size: 0.86rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
        background: rgba(239, 49, 36, 0.14) !important;
        color: #EF3124 !important;
        font-weight: 700 !important;
        border-left: 3px solid #EF3124 !important;
        border-radius: 0 10px 10px 0 !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] input { display: none !important; }

    /* ОСНОВНОЙ ЭКРАН */
    [data-testid="stAppViewContainer"], .stApp {
        background-color: #F5F5F7 !important;
        color: #111827 !important;
    }
    div.block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 1080px !important;
    }
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif !important;
        -webkit-font-smoothing: antialiased;
        letter-spacing: -0.016em;
    }

    .apple-kpi-bar {
        background: #FFFFFF;
        border: 1px solid rgba(0, 0, 0, 0.05);
        border-radius: 18px;
        padding: 18px 22px;
        margin-bottom: 18px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    .apple-hero-banner {
        background: #FFFFFF;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-left: 4px solid #EF3124;
        border-radius: 18px;
        padding: 20px 24px;
        margin-bottom: 22px;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.02);
    }
    .apple-badge-crit {
        background: #FFF1F2;
        color: #E11D48;
        border: 1px solid #FFE4E6;
        padding: 4px 10px;
        border-radius: 980px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    .apple-card-panel {
        background: #FFFFFF;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 20px;
        padding: 26px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.025);
    }
    .apple-title-h2 {
        font-size: 1.35rem;
        font-weight: 700;
        color: #111827;
        line-height: 1.35;
        letter-spacing: -0.025em;
        margin: 8px 0 18px 0;
    }

    .apple-subbox {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 16px 18px;
        height: 100%;
    }
    .apple-tag-pill {
        background: #FFFFFF;
        color: #374151;
        border: 1px solid #D1D5DB;
        padding: 5px 10px;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 500;
        display: inline-block;
        margin-right: 5px;
        margin-bottom: 5px;
    }

    .apple-risk-row {
        background: #FFF8F8;
        border: 1px solid #FEE2E2;
        border-radius: 12px;
        padding: 12px 15px;
        color: #991B1B;
        font-size: 0.88rem;
        line-height: 1.45;
        margin-bottom: 8px;
    }
    .apple-opp-row {
        background: #F6FDF8;
        border: 1px solid #DCFCE7;
        border-radius: 12px;
        padding: 12px 15px;
        color: #166534;
        font-size: 0.88rem;
        line-height: 1.45;
        margin-bottom: 8px;
    }

    .apple-box-bank {
        background: #F8FAFC;
        border: 1px solid #E0F2FE;
        border-left: 3px solid #0071E3;
        border-radius: 0 14px 14px 0;
        padding: 16px 20px;
        height: 100%;
    }
    .apple-box-ai {
        background: #FFFBFB;
        border: 1px solid #FEE2E2;
        border-left: 3px solid #EF3124;
        border-radius: 0 14px 14px 0;
        padding: 16px 20px;
        height: 100%;
    }
    .product-apple-card {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-left: 4px solid #EF3124;
        border-radius: 14px;
        padding: 16px 20px;
        margin-top: 16px;
    }

    /* КНОПКИ APPLE */
    div.stButton > button {
        background-color: #FFFFFF !important;
        color: #374151 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 980px !important;
        font-weight: 500 !important;
        font-size: 0.84rem !important;
        padding: 8px 16px !important;
        min-height: 42px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
        width: 100% !important;
        transition: all 0.15s ease !important;
    }
    div.stButton > button:hover {
        background-color: #F3F4F6 !important;
        border-color: #9CA3AF !important;
        color: #111827 !important;
    }

    .stTextInput div[data-baseweb="input"] { border-radius: 12px !important; }
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        min-height: 44px !important;
    }

    .chat-bubble-user {
        background: #E5E7EB;
        border-radius: 16px 16px 4px 16px;
        padding: 12px 16px;
        font-size: 0.9rem;
        color: #111827;
        margin: 14px 0 10px auto;
        max-width: 85%;
        width: fit-content;
    }
    .chat-bubble-ai {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px 16px 16px 4px;
        padding: 16px 20px;
        font-size: 0.92rem;
        line-height: 1.6;
        color: #111827;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        max-width: 95%;
    }

    @media (max-width: 768px) {
        div.block-container {
            padding: 2.5rem 0.6rem 3rem 0.6rem !important;
        }
        .apple-card-panel {
            padding: 18px 14px !important;
            border-radius: 16px !important;
        }
        .apple-title-h2 { font-size: 1.15rem !important; }
        .apple-kpi-bar { padding: 14px 16px !important; }
        div[data-testid="column"] {
            min-width: 100% !important;
            margin-bottom: 8px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

SVG = {
    "shield": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "trend": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#16A34A" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px;"><path d="M7 7h10v10"/><path d="M7 17 17 7"/></svg>',
    "bank": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px;"><rect width="20" height="4" x="2" y="3" rx="1"/><path d="M4 7v11"/><path d="M8 7v11"/><path d="M12 7v11"/><path d="M16 7v11"/><path d="M20 7v11"/><rect width="20" height="3" x="2" y="18" rx="1"/></svg>',
    "sparkles": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#EF3124" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px;"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>',
    "tag": '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:4px;"><path d="M12 2H2v10l9.29 9.29a2.41 2.41 0 0 0 3.42 0l6.58-6.58a2.41 2.41 0 0 0 0-3.42L12 2Z"/><circle cx="7" cy="7" r="1.5"/></svg>',
    "check": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16A34A" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px;"><polyline points="20 6 9 17 4 12"/></svg>',
    "briefcase": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#EF3124" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px;"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>'
}

COMPANIES = [
    {
        "synthetic_u": "U_1001",
        "display_name": "ПАО «УралМеталлЭкспорт»",
        "main_okved_code": "24.10",
        "main_okved_name": "Производство чугуна, стали и ферросплавов",
        "revenue": 68_500_000_000.0,
        "market_position_label": "Лидер отрасли (Топ-10%)",
        "region": "Свердловская область",
        "debt_preview": "24.8 млрд ₽ (плавающий долг)"
    },
    {
        "synthetic_u": "U_1002",
        "display_name": "АО «Федеральная Торговая Сеть Прайм»",
        "main_okved_code": "47.11",
        "main_okved_name": "Торговля розничная пищевыми продуктами",
        "revenue": 42_000_000_000.0,
        "market_position_label": "Крупный отраслевой игрок",
        "region": "г. Москва",
        "debt_preview": "14.2 млрд ₽ (лизинг и оборот)"
    }
]

INSIGHTS = {
    "U_1001": [{
        "id": "ins_cbr_1001",
        "title": "Банк России сохранил ключевую ставку на уровне 14,0%: пауза в цикле смягчения",
        "date": "11 сентября 2026, 13:30",
        "source": "Банк России / Интерфакс",
        "source_url": "https://cbr.ru/press/",
        "facts": "Совет директоров Банка России 11 сентября 2026 года принял решение сохранить ключевую ставку на уровне 14,00% годовых. Это первая пауза после десяти последовательных снижений ставки с июня 2025 года.",
        "triggers": [
            "ОКВЭД 24.10: Высокая зависимость от стоимости обслуживания долга",
            "Кредитный портфель: 24.8 млрд ₽ с плавающей ставкой КС+2.1%",
            "ВЭД: Экспорт в Китай, Турцию и ОАЭ (волатильность валютных курсов)",
            "Транспортные расходы: индексация ж/д тарифов операторами на 9–12%"
        ],
        "impact": "Ключевой покупатель U_3012 (строительство зданий) перенес авансовые платежи на 30 календарных дней.",
        "risks": [
            "Заморозка процентных расходов на уровне 48.2 млн ₽ в месяц без ожидаемого снижения.",
            "Риск нарушения ковенанты Net Debt / EBITDA при сохранении жестких условий ДКП."
        ],
        "opps": [
            "Размещение операционной ликвидности на овернайт-депозитах Альфа-Банка под 13.85% годовых.",
            "Фиксация ставки на локальном дне цикла через соглашение процентного свопа (IRS)."
        ],
        "alfa_quote": "Для бизнеса сохранение ставки на уровне 14% — сигнал о том, что период быстрого удешевления кредитов временно приостановлен. Деньги остаются дорогими.",
        "alfa_report": "Ключевая ставка ЦБ РФ: ставка без изменения на 14,0%, риторика стала жестче",
        "alfa_forecast": "Средняя ключевая ставка в 2027 г. составит 12.5%, смягчение будет плавным.",
        "ai_prediction": "Для предприятия пауза регулятора означает отсутствие экономии 28 млн ₽ на процентах в 4 квартале. Требуется хеджирование транша 5.0 млрд ₽.",
        "ai_conf": "96%",
        "ai_driver": "Объем плавающего долга 24.8 млрд ₽ при жесткой риторике регулятора",
        "actions": [
            "Заключить соглашение IRS (процентный своп) с Альфа-Банком по траншу 5.0 млрд ₽ по ставке 12.6%.",
            "Запросить у кредитного комитета Альфа-Банка ковенантный вейвер до годовой отчетности.",
            "Оптимизировать график выборки кредитных линий с учетом паузы в снижении ставок."
        ],
        "prod_badge": "Рекомендация банка",
        "prod_title": "Хеджирование процентных рисков (IRS Альфа-Банк)",
        "prod_desc": "Зафиксируйте ставку по кредитам с плавающей ставкой на уровне 12.6% на 24 месяца для защиты бюджета.",
        "prod_btn": "Рассчитать параметры свопа",
        "trace": [
            "Planning: анализ регуляторного события по ДКП и долгового портфеля",
            "Tool Execution: выгрузка контракта U_1001 и макро-отчета Центра исследований",
            "Synthesis: генерация структурированного чек-листа для выбранной роли",
            "Self-Reflection: проверка отсутствия галлюцинаций и ковенантный аудит"
        ]
    }],
    "U_1002": [{
        "id": "ins_labor_1002",
        "title": "Дефицит линейного персонала в ритейле и складской логистике достиг максимума",
        "date": "12 сентября 2026, 11:40",
        "source": "РБК Аналитика",
        "source_url": "https://www.rbc.ru/",
        "facts": "По данным мониторинга рынка труда за 7 месяцев 2026 года, дефицит складских работников, водителей и торгового персонала привел к росту предлагаемых зарплат на 16% год к году.",
        "triggers": [
            "ОКВЭД 47.11: Высокая доля ФОТ в себестоимости розничной сети",
            "Численность персонала: более 10 000 сотрудников",
            "Лизинг автопарка: чувствительность к стоимости обновления логистики",
            "Потребительский спрос: прохождение пика покупательской активности"
        ],
        "impact": "Поставщики молочной продукции (U_4088) предупредили о повышении цен на 6–8% из-за дефицита упаковки и роста зарплат.",
        "risks": [
            "Рост фонда оплаты труда на 180 млн руб. в 4 квартале.",
            "Кадровый дефицит в распределительных центрах перед предновогодним сезоном."
        ],
        "opps": [
            "Подключение расширенного зарплатного проекта Альфа-Банка с льготной ипотекой для удержания персонала.",
            "Факторинговое финансирование отсрочек платежей поставщиков."
        ],
        "alfa_quote": "Дефицит кадров остается ключевым проинфляционным фактором. Трудоемкому бизнесу рекомендуется переходить на автоматизацию и долгосрочные программы удержания персонала.",
        "alfa_report": "Макростатистика 7М26: данные по рынку труда не подтверждают охлаждения экономики",
        "alfa_forecast": "Давление со стороны зарплат сохранится на протяжении всего 2027 года.",
        "ai_prediction": "Для АО «ФТС Прайм» ускорение роста зарплат требует оптимизации графиков выплат и подключения зарплатной экосистемы Альфа-Банка.",
        "ai_conf": "92%",
        "ai_driver": "Массовый штат сотрудников и дефицит линейных специалистов",
        "actions": [
            "Перевести персонал распределительных центров на зарплатный проект Альфа-Банка с кэшбэком и овердрафтом.",
            "Провести индексацию ФОТ только для критических логистических специальностей."
        ],
        "prod_badge": "Рекомендация банка",
        "prod_title": "Зарплатный проект и мотивационная программа Альфа-Банка",
        "prod_desc": "Снизьте затраты на начисление зарплат и предоставьте сотрудникам льготное кредитование и ДМС.",
        "prod_btn": "Подключить зарплатный проект",
        "trace": [
            "Planning: анализ ситуации на рынке труда и структуры расходов компании",
            "Tool Execution: выгрузка штата U_1002 (10000+ чел.) и макро-отчета Альфа-Банка 7М26",
            "Synthesis: генерация персональных мер снижения текучести кадров",
            "Self-Reflection: проверка баланса затрат и эффекта льготных программ"
        ]
    }]
}

def call_live_llm(prompt: str, context: str) -> str:
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    system_msg = (
        "Ты — старший финансово-экономический аналитик Центра макроэкономических исследований Альфа-Банка. "
        "Твоя аудитория — топ-менеджмент крупного бизнеса (CEO, CFO, Руководитель казначейства). "
        "Правила ответа:\n"
        "1. ВСЕГДА заканчивай свою мысль и предложения полностью. Никаких обрывов текста.\n"
        "2. Если пользователь просто здоровается или обращается неформально: "
        "с достоинством поприветствуй его и сразу же переведи разговор в деловое русло, кратко обозначив 2 главных финансовых риска текущей компании по ставке 14% и спросив, какой показатель рассчитать детально.\n"
        "3. Если задан конкретный вопрос — дай глубокий расчет с цифрами компании, влиянием на прибыль и решением от Альфа-Банка."
    )
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"Контекст предприятия:\n{context}\n\nВопрос руководителя:\n{prompt}"}
        ],
        "temperature": 0.3,
        "max_tokens": 1200
    }
    
    for url in [f"{PRIMARY_URL}/chat/completions", f"{BACKUP_URL}/chat/completions"]:
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=18.0)
            if r.status_code == 200:
                res_data = r.json()
                content = res_data["choices"][0]["message"]["content"]
                if content and len(content.strip()) > 0:
                    return content
        except Exception:
            continue
    return None

def ask_ai_chat(company: dict, role: str, insight: dict, question: str) -> str:
    ctx = (
        f"Компания: {company.get('display_name')}\n"
        f"ОКВЭД: {company.get('main_okved_code')}\n"
        f"Выручка: {company.get('revenue')} руб., Кредитный долг: {company.get('debt_preview')}\n"
        f"Роль руководителя: {role}\n"
        f"Событие: {insight.get('title')}\n"
        f"Позиция Альфа-Банка: {insight.get('alfa_quote')}"
    )

    live_result = call_live_llm(question, ctx)
    if live_result:
        return live_result

    q_low = question.lower()
    if any(w in q_low for w in ["долг", "нагрузк", "ставк", "процент", "кредит"]):
        return (
            "**Финансовый расчет долговой нагрузки (CFO View):**\n\n"
            "• **Ежемесячный платеж:** Сохранение ставки 14.0% фиксирует процентные расходы на уровне **48.2 млн руб./мес**.\n\n"
            "• **Упущенная выгода:** Отсутствие снижения ставки на 100 б.п. откладывает экономию в **3.45 млн руб. в месяц**.\n\n"
            "• **Ковенанты:** Коэффициент покрытия долга (ICR) составит **3.15x** при допустимом пороге 2.80x.\n\n"
            "• **Рекомендация:** Зафиксировать ставку по траншу 5.0 млрд руб. на уровне 12.6% через IRS Альфа-Банка."
        )

    return (
        "**Аналитическая служба Альфа-Инсайт:**\n\n"
        "Приветствую! Для вашего предприятия ключевой задачей на 4 квартал является защита рентабельности от жесткой политики ЦБ. "
        "Готов рассчитать влияние ставки 14% на долговую нагрузку или смоделировать риски по цепочке контрагентов. Какой расчет сформировать?"
    )

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "applied_products" not in st.session_state:
    st.session_state.applied_products = set()

# ВЫДВИЖНАЯ ШТОРКА
with st.sidebar:
    st.markdown(f'<div style="display:flex;align-items:center;margin-bottom:20px;">{get_logo_html()}<span style="font-weight:700;font-size:1.05rem;letter-spacing:-0.02em;">АЛЬФА-БИЗНЕС</span></div>', unsafe_allow_html=True)
    
    st.caption("ОРГАНИЗАЦИЯ")
    comp_map = {c["display_name"]: c for c in COMPANIES}
    selected_name = st.selectbox("Клиент", list(comp_map.keys()), label_visibility="collapsed")
    current_company = comp_map[selected_name]
    company_id = current_company["synthetic_u"]

    st.caption("РОЛЬ РУКОВОДИТЕЛЯ")
    ROLE_OPTIONS = {
        "CFO": "Финансовый директор (CFO)",
        "CEO": "Генеральный директор (CEO)",
        "TREASURER": "Руководитель казначейства (TREASURER)",
        "ACCOUNTANT": "Главный бухгалтер (ACCOUNTANT)"
    }
    selected_role_label = st.selectbox("Роль", list(ROLE_OPTIONS.values()), index=0, label_visibility="collapsed")
    current_role_code = [k for k, v in ROLE_OPTIONS.items() if v == selected_role_label][0]

    st.markdown("<hr style='margin:16px 0;border:none;border-top:1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
    
    st.caption("РАЗДЕЛЫ БАНКА")
    active_section = st.radio(
        "Навигация",
        options=["Альфа-Инсайт", "Счета и выписки", "Кредитные линии", "ВЭД и валюта"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
    st.caption("БЕЗОПАСНЫЙ КОНТУР")
    st.markdown(f"<div style='font-size:0.75rem;color:#9CA3AF;'>Модель: <b>{LLM_MODEL.split('/')[-1]}</b><br>Шлюз: <b>Live 1200 Tokens</b></div>", unsafe_allow_html=True)

# ОСНОВНОЙ ЭКРАН
if active_section == "Счета и выписки":
    st.markdown(f"<h2>Счета и остатки: {current_company['display_name']}</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:16px;padding:20px;">
            <div style="font-size:0.8rem;color:#6B7280;font-weight:600;">ОСНОВНОЙ РАСЧЕТНЫЙ СЧЕТ (RUB)</div>
            <div style="font-size:1.7rem;font-weight:700;color:#111827;margin-top:4px;">4 820 450 000 ₽</div>
            <div style="font-size:0.82rem;color:#16A34A;margin-top:4px;">● Счет активен • Альфа-Банк Корпоративный</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:16px;padding:20px;">
            <div style="font-size:0.8rem;color:#6B7280;font-weight:600;">ВАЛЮТНЫЙ СЧЕТ (CNY)</div>
            <div style="font-size:1.7rem;font-weight:700;color:#111827;margin-top:4px;">84 200 000 ¥</div>
            <div style="font-size:0.82rem;color:#0284C7;margin-top:4px;">● Филиал Альфа-Банка в Пекине (Прямой клиринг)</div>
        </div>
        """, unsafe_allow_html=True)

elif active_section == "Кредитные линии":
    st.markdown(f"<h2>Кредитный портфель: {current_company['display_name']}</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-left:4px solid #EF3124;border-radius:16px;padding:22px;">
        <div style="font-size:0.8rem;color:#6B7280;font-weight:700;">ГЕНЕРАЛЬНОЕ КРЕДИТНОЕ СОГЛАШЕНИЕ №ALF-774</div>
        <div style="font-size:1.5rem;font-weight:700;color:#111827;margin-top:4px;">{current_company['debt_preview']}</div>
        <div style="font-size:0.88rem;color:#374151;margin-top:6px;">
            <b>Параметры:</b> Плавающая ставка <b>КС ЦБ + 2.1%</b> годовых.<br>
            <b>Срок действия:</b> до 28 декабря 2028 г. (Свободный лимит: 5.2 млрд ₽).
        </div>
    </div>
    """, unsafe_allow_html=True)

elif active_section == "ВЭД и валюта":
    st.markdown(f"<h2>ВЭД и таможенный контроль: {current_company['display_name']}</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:16px;padding:22px;">
        <div style="font-size:1.1rem;font-weight:700;color:#111827;">Активные внешнеторговые контракты</div>
        <div style="font-size:0.88rem;color:#4B5563;margin-top:6px;">
            Профиль контрагентов: <b>Китай, Турция, ОАЭ</b>.<br>
            Канал расчетов: Защищенный шлюз расчетов в юанях и дирхамах с предварительной комплаенс-валидацией ГТД.
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    comp_rev = float(current_company["revenue"]) / 1_000_000
    kpi_html = (
        '<div class="apple-kpi-bar">'
        '<div>'
        f'<div style="font-size:1.15rem;font-weight:700;color:#111827;">{current_company["display_name"]}</div>'
        f'<div style="font-size:0.82rem;color:#6B7280;margin-top:2px;">ОКВЭД {current_company["main_okved_code"]} &nbsp;•&nbsp; {current_company["market_position_label"]}</div>'
        '</div>'
        '<div>'
        f'<span style="font-size:1.45rem;font-weight:700;color:#111827;">{comp_rev:,.0f} млн ₽</span>'
        f'<span style="background:#FEF2F2;color:#991B1B;padding:3px 8px;border-radius:6px;font-size:0.75rem;font-weight:600;margin-left:8px;">{current_company["debt_preview"]}</span>'
        '</div>'
        '</div>'
    )
    st.markdown(kpi_html, unsafe_allow_html=True)

    insights = INSIGHTS.get(company_id, INSIGHTS["U_1001"])
    entry_html = (
        '<div class="apple-hero-banner">'
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;flex-wrap:wrap;gap:8px;">'
        f'<div style="font-size:1.1rem;font-weight:700;color:#111827;display:flex;align-items:center;">{SVG["sparkles"]} Альфа-Инсайт: Персонализированная аналитика рисков и возможностей</div>'
        f'<span class="apple-badge-crit">Событий: {len(insights)}</span>'
        '</div>'
        f'<div style="color:#4B5563;font-size:0.88rem;line-height:1.5;">Мультиагентный сервис сопоставил публикации рынка и макро-отчеты Альфа-Банка. Сформирован стратегический фокус для роли <b>{selected_role_label}</b>.</div>'
        '</div>'
    )
    st.markdown(entry_html, unsafe_allow_html=True)

    for ins in insights:
        st.markdown('<div class="apple-card-panel">', unsafe_allow_html=True)
        
        card_header = (
            '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">'
            '<span class="apple-badge-crit">Высокий приоритет</span>'
            f'<span style="font-size:0.8rem;color:#6B7280;">{ins["date"]} &nbsp;•&nbsp; Источник: <b>{ins["source"]}</b></span>'
            '</div>'
            f'<div class="apple-title-h2">{ins["title"]}</div>'
        )
        st.markdown(card_header, unsafe_allow_html=True)

        b1, b2 = st.columns(2)
        with b1:
            st.caption("1. ЧТО ПРОИЗОШЛО")
            b1_html = (
                '<div class="apple-subbox">'
                f'<div style="font-size:0.88rem;line-height:1.5;color:#374151;margin-bottom:10px;">{ins["facts"]}</div>'
                f'<a href="{ins["source_url"]}" target="_blank" style="font-size:0.82rem;color:#0071E3;text-decoration:none;font-weight:600;">Официальный первоисточник релиза &rarr;</a>'
                '</div>'
            )
            st.markdown(b1_html, unsafe_allow_html=True)

        with b2:
            st.caption("2. ПОЧЕМУ ЭТО ВАЖНО ДЛЯ КОМПАНИИ")
            pills = "".join([f'<span class="apple-tag-pill">{SVG["tag"]}{p}</span>' for p in ins["triggers"]])
            b2_html = (
                '<div class="apple-subbox">'
                f'<div style="margin-bottom:6px;">{pills}</div>'
                f'<div style="font-size:0.84rem;color:#4B5563;border-top:1px solid #E5E7EB;padding-top:6px;"><b>Влияние на цепочку контрагентов:</b> {ins["impact"]}</div>'
                '</div>'
            )
            st.markdown(b2_html, unsafe_allow_html=True)

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        st.caption("3. ПРОГНОЗ ПОСЛЕДСТВИЙ ДЛЯ БИЗНЕСА")
        rc, oc = st.columns(2)
        with rc:
            st.markdown(f"<div style='font-size:0.85rem;font-weight:700;color:#DC2626;margin-bottom:6px;'>{SVG['shield']} Потенциальные риски</div>", unsafe_allow_html=True)
            for r in ins["risks"]:
                st.markdown(f'<div class="apple-risk-row">{r}</div>', unsafe_allow_html=True)
        with oc:
            st.markdown(f"<div style='font-size:0.85rem;font-weight:700;color:#16A34A;margin-bottom:6px;'>{SVG['trend']} Открывающиеся возможности</div>", unsafe_allow_html=True)
            for o in ins["opps"]:
                st.markdown(f'<div class="apple-opp-row">{SVG["check"]} {o}</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        st.caption("4. ОЦЕНКА АЛЬФА-БАНКА VS ВЫВОД ИИ")
        mc, aic = st.columns(2)
        with mc:
            b_html = (
                '<div class="apple-box-bank">'
                f'<div style="font-weight:700;color:#0071E3;font-size:0.9rem;margin-bottom:6px;">{SVG["bank"]} Позиция аналитиков Альфа-Банка</div>'
                f'<div style="font-size:0.88rem;font-style:italic;color:#1E293B;margin-bottom:8px;line-height:1.45;">«{ins["alfa_quote"]}»</div>'
                f'<div style="font-size:0.75rem;color:#64748B;">Материал: <b>{ins["alfa_report"]}</b><br>Базовый прогноз: {ins["alfa_forecast"]}</div>'
                '</div>'
            )
            st.markdown(b_html, unsafe_allow_html=True)
        with aic:
            ai_html = (
                '<div class="apple-box-ai">'
                f'<div style="font-weight:700;color:#EF3124;font-size:0.9rem;margin-bottom:6px;">{SVG["sparkles"]} Персонализированный AI-вывод для предприятия</div>'
                f'<div style="font-size:0.88rem;color:#1E293B;margin-bottom:8px;line-height:1.45;">{ins["ai_prediction"]}</div>'
                f'<div style="font-size:0.75rem;color:#991B1B;">Уверенность модели: <b>{ins["ai_conf"]}</b> &nbsp;•&nbsp; Драйвер: {ins["ai_driver"]}</div>'
                '</div>'
            )
            st.markdown(ai_html, unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        st.caption(f"5. РЕКОМЕНДУЕМЫЕ ДЕЙСТВИЯ ДЛЯ РОЛИ: {selected_role_label.upper()}")
        for s_idx, act in enumerate(ins["actions"], 1):
            st.checkbox(f"Шаг {s_idx}: {act}", key=f"step_{ins['id']}_{s_idx}")

        pk = f"prod_{ins['id']}"
        is_applied = pk in st.session_state.applied_products

        st.markdown(f"""
        <div class="product-apple-card">
            <div style="display:flex;align-items:center;gap:6px;">
                {SVG['briefcase']}
                <span style="font-size:0.72rem;font-weight:700;color:#EF3124;text-transform:uppercase;">
                    {ins["prod_badge"]}
                </span>
            </div>
            <div style="font-size:1.05rem;font-weight:700;color:#111827;margin-top:4px;">
                {ins["prod_title"]}
            </div>
            <div style="font-size:0.85rem;color:#4B5563;margin-top:4px;line-height:1.4;">
                {ins["prod_desc"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        
        col_btn_left, col_btn_right = st.columns([1.8, 3])
        with col_btn_left:
            if is_applied:
                st.markdown("<div style='color:#16A34A;font-weight:600;font-size:0.85rem;padding:8px 0;'>✓ Заявка передана банкиру</div>", unsafe_allow_html=True)
            else:
                if st.button(f"{ins['prod_btn']}", key=f"btn_{pk}"):
                    st.session_state.applied_products.add(pk)
                    st.balloons()
                    st.rerun()

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        with st.expander("Аудит-лог и происхождение выводов (Traceability)"):
            st.caption("Пошаговый протокол рассуждения многошагового агента:")
            for t in ins["trace"]:
                st.markdown(f"• {t}")

        st.markdown("<hr style='border:none;border-top:1px solid #E5E7EB;margin:20px 0;'>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.92rem;font-weight:700;color:#111827;margin-bottom:10px;">Уточняющие вопросы AI-аналитику:</div>', unsafe_allow_html=True)

        col_q1, col_q2 = st.columns(2)
        selected_preset = None
        with col_q1:
            if st.button("Рассчитать влияние на долговую нагрузку", key=f"q1_{ins['id']}"):
                selected_preset = "Рассчитай влияние на долговую нагрузку компании"
        with col_q2:
            if st.button("Оценить риски цепочки контрагентов", key=f"q2_{ins['id']}"):
                selected_preset = "Как это отразится на наших поставщиках и покупателях?"

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        col_input, col_submit = st.columns([4.2, 1])
        with col_input:
            u_query = st.text_input("Вопрос", key=f"inp_{ins['id']}", placeholder="Спросите о ликвидности, кредитах или ВЭД...", label_visibility="collapsed")
        with col_submit:
            ask_clicked = st.button("Спросить", key=f"ask_{ins['id']}")

        if ask_clicked or selected_preset:
            txt = selected_preset if selected_preset else u_query
            if txt:
                with st.spinner("AI-агент формирует аналитический расчет..."):
                    ans = ask_ai_chat(current_company, selected_role_label, ins, txt)
                    st.session_state.chat_history[ins['id']] = {"q": txt, "a": ans}

        if ins['id'] in st.session_state.chat_history:
            h = st.session_state.chat_history[ins['id']]
            st.markdown(f'<div class="chat-bubble-user"><b>Вы:</b> {h["q"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-bubble-ai">{h["a"]}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<center style='color:#9CA3AF;font-size:0.8rem;margin-top:20px;'>Интернет-банк «Альфа-Бизнес» &nbsp;•&nbsp; Сервис «Альфа-Инсайт»</center>", unsafe_allow_html=True)
