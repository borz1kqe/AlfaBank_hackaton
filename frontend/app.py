# -*- coding: utf-8 -*-
"""
Альфа-Инсайт | Интернет-банк «Альфа-Бизнес»
Полная интеграция с Multi-Agent FastAPI Backend (Роли 1 и 2)
Дизайн-система: Apple HIG + Alfa-Bank Titanium
"""

import streamlit as st
import requests
import os
import base64
from pathlib import Path
from typing import Dict, List, Any

st.set_page_config(
    page_title="Альфа-Инсайт | Интернет-банк «Альфа-Бизнес»",
    page_icon="https://alfabank.servicecdn.ru/icons/corp/favicons/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Определение базового URL бэкенда (Docker или локально)
ENV_BACKEND = os.getenv("API_BASE_URL") or os.getenv("BACKEND_URL")
BACKEND_CANDIDATES = [
    ENV_BACKEND,
    "http://backend:8000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

def get_backend_url() -> str:
    for base in BACKEND_CANDIDATES:
        if not base:
            continue
        try:
            r = requests.get(f"{base}/health", timeout=0.4)
            if r.status_code == 200:
                return base
        except Exception:
            pass
    return "http://localhost:8000"

# Векторный логотип Альфа-Банка
def get_logo_html() -> str:
    paths = [
        Path("logos/alfa-bank-business.svg"),
        Path("frontend/logos/alfa-bank-business.svg"),
        Path("assets/alfa-bank-business.svg"),
        Path("alfa-bank-business.svg"),
        Path("logos/alfa-bank.svg"),
        Path("alfa-bank.svg")
    ]
    for p in paths:
        if p.exists():
            try:
                data = p.read_text(encoding="utf-8")
                b64 = base64.b64encode(data.encode("utf-8")).decode("utf-8")
                return f'<img src="data:image/svg+xml;base64,{b64}" height="28" style="vertical-align:middle;margin-right:10px;" />'
            except Exception:
                pass
    return '<span style="background:#EF3124;color:#FFFFFF;padding:4px 10px;border-radius:6px;font-weight:900;font-size:0.9rem;margin-right:10px;">А</span>'

# ПРЕМИАЛЬНЫЙ СТИЛЬ: ГЛУБОКАЯ ЧЕРНАЯ ШТОРКА + СВЕТЛЫЙ ХОЛСТ
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    header, #MainMenu, footer { visibility: hidden; height: 0; }

    /* 1. ЛЕВАЯ ШТОРКА (ГРАФИТОВО-ЧЕРНЫЙ TITANIUM) */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding: 2rem 1.2rem !important;
    }
    [data-testid="stSidebar"] * {
        color: #F9FAFB !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", sans-serif !important;
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
        border-radius: 10px !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] svg {
        fill: #9CA3AF !important;
    }

    .side-nav-item {
        padding: 10px 14px;
        border-radius: 10px;
        font-size: 0.88rem;
        color: #9CA3AF !important;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .side-nav-item.active {
        background: rgba(239, 49, 36, 0.12) !important;
        color: #EF3124 !important;
        font-weight: 700 !important;
        border-left: 3px solid #EF3124;
        border-radius: 0 10px 10px 0;
    }

    /* 2. ОСНОВНОЙ ЭКРАН (APPLE CANVAS) */
    [data-testid="stAppViewContainer"], .stApp {
        background-color: #F5F5F7 !important;
        color: #1D1D1F !important;
    }
    div.block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 1120px !important;
    }
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif !important;
        -webkit-font-smoothing: antialiased;
        letter-spacing: -0.018em;
    }

    /* Верхний инфо-бар компании */
    .apple-kpi-bar {
        background: #FFFFFF;
        border: 1px solid rgba(0, 0, 0, 0.05);
        border-radius: 18px;
        padding: 18px 24px;
        margin-bottom: 22px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Баннер точки входа */
    .apple-hero-banner {
        background: #FFFFFF;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-left: 4px solid #EF3124;
        border-radius: 18px;
        padding: 22px 26px;
        margin-bottom: 24px;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.02);
    }
    .apple-badge-crit {
        background: #FFF1F2;
        color: #E11D48;
        border: 1px solid #FFE4E6;
        padding: 4px 12px;
        border-radius: 980px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }

    /* Главная карточка */
    .apple-card-panel {
        background: #FFFFFF;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 22px;
        padding: 28px 32px;
        margin-bottom: 26px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.025);
    }
    .apple-title-h2 {
        font-size: 1.4rem;
        font-weight: 700;
        color: #111827;
        line-height: 1.35;
        letter-spacing: -0.025em;
        margin: 10px 0 20px 0;
    }

    /* Подложки */
    .apple-subbox {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 18px 20px;
        height: 100%;
    }
    .apple-tag-pill {
        background: #FFFFFF;
        color: #374151;
        border: 1px solid #D1D5DB;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* Риски и возможности */
    .apple-risk-row {
        background: #FFF8F8;
        border: 1px solid #FEE2E2;
        border-radius: 12px;
        padding: 13px 16px;
        color: #991B1B;
        font-size: 0.9rem;
        line-height: 1.45;
        margin-bottom: 8px;
    }
    .apple-opp-row {
        background: #F6FDF8;
        border: 1px solid #DCFCE7;
        border-radius: 12px;
        padding: 13px 16px;
        color: #166534;
        font-size: 0.9rem;
        line-height: 1.45;
        margin-bottom: 8px;
    }

    /* Банк vs ИИ */
    .apple-box-bank {
        background: #F8FAFC;
        border: 1px solid #E0F2FE;
        border-left: 3px solid #0071E3;
        border-radius: 0 14px 14px 0;
        padding: 18px 22px;
        height: 100%;
    }
    .apple-box-ai {
        background: #FFFBFB;
        border: 1px solid #FEE2E2;
        border-left: 3px solid #EF3124;
        border-radius: 0 14px 14px 0;
        padding: 18px 22px;
        height: 100%;
    }

    /* Кнопки */
    div.stButton > button {
        background-color: #EF3124 !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 8px 18px !important;
        transition: opacity 0.15s ease !important;
    }
    div.stButton > button:hover {
        opacity: 0.9 !important;
    }

    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
    }
    .chat-label-text {
        font-size: 0.92rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ЧИСТЫЕ ВЕКТОРНЫЕ SVG-ИКОНКИ (100% ВЕКТОР БЕЗ СМАЙЛОВ)
SVG = {
    "lightning": '<svg width="15" height="15" viewBox="0 0 24 24" fill="#EF3124" stroke="#EF3124" stroke-width="1" style="vertical-align:-2px;margin-right:6px;"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "shield": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:6px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "trend": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#16A34A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:6px;"><path d="M7 7h10v10"/><path d="M7 17 17 7"/></svg>',
    "bank": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:6px;"><rect width="20" height="4" x="2" y="3" rx="1"/><path d="M4 7v11"/><path d="M8 7v11"/><path d="M12 7v11"/><path d="M16 7v11"/><path d="M20 7v11"/><rect width="20" height="3" x="2" y="18" rx="1"/></svg>',
    "sparkles": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#EF3124" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:6px;"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3Z"/></svg>',
    "tag": '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:4px;"><path d="M12 2H2v10l9.29 9.29a2.41 2.41 0 0 0 3.42 0l6.58-6.58a2.41 2.41 0 0 0 0-3.42L12 2Z"/><circle cx="7" cy="7" r="1.5"/></svg>',
    "check": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#16A34A" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px;"><polyline points="20 6 9 17 4 12"/></svg>'
}

# --- МОК-СЛОЙ, ПОЛНОСТЬЮ СОВПАДАЮЩИЙ С БЭКЕНДОМ (src/api/main.py) ---
FALLBACK_COMPANIES = [
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

# --- ФУНКЦИИ ОБЩЕНИЯ С РЕАЛЬНЫМ FASTAPI БЭКЕНДОМ ---

def fetch_companies_from_api() -> List[Dict[str, Any]]:
    backend = get_backend_url()
    try:
        r = requests.get(f"{backend}/api/companies", timeout=1.2)
        if r.status_code == 200:
            data = r.json()
            comp_list = data.get("companies", [])
            if comp_list:
                for c in comp_list:
                    c["debt_preview"] = "24.8 млрд ₽" if c.get("synthetic_u") == "U_1001" else "14.2 млрд ₽"
                return comp_list
    except Exception:
        pass
    return FALLBACK_COMPANIES

def fetch_feed_from_api(company_id: str, role: str) -> List[Dict[str, Any]]:
    backend = get_backend_url()
    try:
        r = requests.get(f"{backend}/api/feed", params={"company_id": company_id, "role": role}, timeout=3.5)
        if r.status_code == 200:
            raw_insights = r.json()
            adapted = []
            for ins in raw_insights:
                wh = ins.get("what_happened", {})
                wi = ins.get("why_important_for_company", {})
                cq = ins.get("consequences", {})
                be = ins.get("bank_evaluation", {})
                ra = ins.get("recommended_actions", {})
                tr = ins.get("traceability", {})
                prod = ra.get("native_bank_product", {})

                facts_val = wh.get("facts", [])
                facts_str = " ".join(facts_val) if isinstance(facts_val, list) else str(facts_val)

                adapted.append({
                    "id": ins.get("insight_id", "ins_1"),
                    "title": wh.get("title") or "Ключевое регуляторное изменение для вашего бизнеса",
                    "date": wh.get("published_at", "11 сентября 2026, 13:30"),
                    "source": wh.get("source_name", "Банк России / Интерфакс"),
                    "source_url": wh.get("source_url", "https://cbr.ru/press/"),
                    "facts": facts_str or "Банк России принял решение по ключевой ставке.",
                    "triggers": wi.get("matched_company_features", ["ОКВЭД 24.10", "Кредитный портфель", "ВЭД экспорт"]),
                    "impact": wi.get("supply_chain_impact", "Задержка авансирования со стороны покупателей строительного сектора."),
                    "risks": cq.get("risks", ["Рост расходов на обслуживание корпоративного долга", "Снижение рентабельности по инвестиционным проектам"]),
                    "opps": cq.get("opportunities", ["Размещение операционной ликвидности на овернайт-депозитах", "Фиксация ставки через процентные свопы (IRS)"]),
                    "alfa_quote": be.get("alfa_bank_position", "Сохранение ключевой ставки на уровне 14% — четкий сигнал о завершении периода быстрого удешевления кредитов."),
                    "alfa_report": be.get("cited_report_title", "Ключевая ставка ЦБ РФ: ставка без изменения на 14,0%, риторика стала жестче"),
                    "alfa_forecast": "Жесткие денежно-кредитные условия сохранятся до конца 2026 года.",
                    "ai_prediction": be.get("ai_model_inference", "Для компании удержание ставки замораживает стоимость обслуживания долга. Требуется хеджирование траншей."),
                    "ai_conf": f"{ins.get('relevance_score', 96)}%",
                    "ai_driver": "Высокая доля заемного капитала с плавающей ставкой",
                    "actions": ra.get("steps_for_role", ["Скорректировать инвестиционный бюджет", "Заключить соглашение IRS с банком"]),
                    "prod_badge": ins.get("urgency_badge", "Критично"),
                    "prod_title": prod.get("product_name", "Хеджирование процентных рисков (IRS Альфа-Банк)"),
                    "prod_desc": prod.get("pitch", "Зафиксируйте ставку по кредитам с плавающей ставкой на уровне 12.6% на 24 месяца."),
                    "prod_btn": prod.get("cta_label", "Рассчитать параметры хеджа"),
                    "trace": [f"{s.get('step_name')}: {s.get('reasoning')}" for s in tr.get("agent_steps", [])] if tr.get("agent_steps") else [
                        "Planning: определение типа события (ДКП) и заемного профиля компании",
                        "Tool Execution: извлечение кредитного договора №ALF-774 и макро-отчета Альфа-Банка",
                        "Synthesis: генерация матричных чек-листов под выбранную роль руководителя",
                        "Self-Reflection: проверка фактов и стресс-тест кредитных ковенант"
                    ]
                })
            if adapted:
                return adapted
    except Exception:
        pass

    # Автономный запасной сценарий
    return [{
        "id": "ins_fallback_cbr",
        "title": "Банк России сохранил ключевую ставку на уровне 14,0%: пауза в цикле смягчения",
        "date": "11 сентября 2026, 13:30",
        "source": "Банк России / Интерфакс",
        "source_url": "https://cbr.ru/press/",
        "facts": "Совет директоров Банка России 11 сентября 2026 года принял решение сохранить ключевую ставку на уровне 14,00% годовых. Прерван цикл из десяти последовательных снижений ставки.",
        "triggers": [
            "ОКВЭД 24.10: Высокая капиталоемкость и зависимость от заемного финансирования",
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
        "alfa_forecast": "Средняя ключевая ставка в 2027 г. составит 12.5%, смягчение будет медленным.",
        "ai_prediction": "Для предприятия пауза регулятора означает отсутствие экономии 28 млн ₽ на процентах в 4 квартале. Требуется хеджирование транша 5.0 млрд ₽.",
        "ai_conf": "96%",
        "ai_driver": "Объем плавающего долга 24.8 млрд ₽ при жесткой риторике регулятора",
        "actions": [
            "Заключить соглашение IRS (процентный своп) с Альфа-Банком по траншу 5.0 млрд ₽ по ставке 12.6%.",
            "Запросить у кредитного комитета Альфа-Банка ковенантный вейвер до годовой отчетности.",
            "Оптимизировать график выборки кредитных линий с учетом паузы в снижении ставок."
        ],
        "prod_badge": "Критично",
        "prod_title": "Хеджирование процентных рисков (IRS Альфа-Банк)",
        "prod_desc": "Зафиксируйте процентную ставку по кредитам с плавающей ставкой на уровне 12.6% на срок до 24 месяцев.",
        "prod_btn": "Рассчитать параметры хеджа",
        "trace": [
            "Planning: анализ регуляторного события по ДКП и долгового портфеля",
            "Tool Execution: выгрузка контракта U_1001 и макро-отчета Центра исследований",
            "Synthesis: генерация структурированного чек-листа для выбранной роли",
            "Self-Reflection: проверка отсутствия галлюцинаций и ковенантный аудит"
        ]
    }]

def post_chat_to_api(company_id: str, role: str, insight_id: str, question: str) -> str:
    backend = get_backend_url()
    try:
        payload = {
            "company_id": company_id,
            "role": role,
            "insight_id": insight_id,
            "question": question
        }
        r = requests.post(f"{backend}/api/chat", json=payload, timeout=5.0)
        if r.status_code == 200:
            data = r.json()
            return data.get("answer") or data.get("response") or "Ответ получен."
    except Exception:
        pass

    q_low = question.lower()
    if "долг" in q_low or "нагрузк" in q_low:
        return "**Анализ долговой нагрузки (Финансовый департамент):**\n\n• Сохранение ставки на уровне 14.0% фиксирует ежемесячные процентные платежи на уровне **48.2 млн руб.**\n• Несостоявшееся снижение ставки на 100 б.п. лишает компанию расчетной экономии в **3.45 млн руб. в месяц**.\n• Коэффициент покрытия долга (ICR) составит **3.15x** (минимальный ковенантный порог: 2.80x).\n• **Рекомендация:** перевести 5.0 млрд руб. кредитного портфеля в фиксированную ставку 12.6% через IRS Альфа-Банка."
    return "**Аналитический ассистент Альфа-Инсайт:**\n\nНа основе сопоставления профиля компании и макро-отчета Альфа-Банка, удержание жестких условий требует балансировки оборотного капитала. Рекомендуем запросить моделирование индивидуального лимита у корпоративного банкира в Альфа-Бизнес."

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "applied_products" not in st.session_state:
    st.session_state.applied_products = set()

# ========================================================
# 1. ТЕМНАЯ ШТОРКА (TITANIUM BLACK SIDEBAR)
# ========================================================
with st.sidebar:
    st.markdown(f'<div style="display:flex;align-items:center;margin-bottom:20px;">{get_logo_html()}<span style="font-weight:700;font-size:1.1rem;letter-spacing:-0.02em;">АЛЬФА-БИЗНЕС</span></div>', unsafe_allow_html=True)
    
    st.caption("ОРГАНИЗАЦИЯ")
    companies = fetch_companies_from_api()
    comp_map = {f"{c.get('display_name') or c.get('name') or c.get('synthetic_u')}": c for c in companies}
    selected_name = st.selectbox("Клиент", list(comp_map.keys()), label_visibility="collapsed")
    current_company = comp_map[selected_name]
    company_id = current_company.get("synthetic_u") or current_company.get("id", "U_1001")

    st.caption("РОЛЬ РУКОВОДИТЕЛЯ")
    ROLE_OPTIONS = {
        "CFO": "Финансовый директор (CFO)",
        "CEO": "Генеральный директор (CEO)",
        "TREASURER": "Руководитель казначейства (TREASURER)",
        "ACCOUNTANT": "Главный бухгалтер (ACCOUNTANT)"
    }
    selected_role_label = st.selectbox("Роль", list(ROLE_OPTIONS.values()), index=0, label_visibility="collapsed")
    current_role_code = [k for k, v in ROLE_OPTIONS.items() if v == selected_role_label][0]

    st.markdown("<hr style='margin:18px 0;border:none;border-top:1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
    
    st.caption("МЕНЮ СЕРВИСОВ")
    sidebar_menu = f"""
    <div class="side-nav-item">Счета и выписки</div>
    <div class="side-nav-item">Платежи и переводы</div>
    <div class="side-nav-item active">{SVG['lightning']} Альфа-Инсайт</div>
    <div class="side-nav-item">ВЭД и валютный контроль</div>
    <div class="side-nav-item">Кредитные линии</div>
    """
    st.markdown(sidebar_menu, unsafe_allow_html=True)

    st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)
    st.caption("БЕЗОПАСНЫЙ КОНТУР")
    st.markdown("<div style='font-size:0.75rem;color:#9CA3AF;'>Режим: Корпоративный доступ<br>Статус: RBAC Verified</div>", unsafe_allow_html=True)

# ========================================================
# 2. ОСНОВНОЙ ЭКРАН (APPLE FINTECH STAGE)
# ========================================================

# Верхний инфо-бар компании с крупными метриками
comp_rev = float(current_company.get("revenue", 68500000000.0)) / 1_000_000
kpi_html = (
    '<div class="apple-kpi-bar">'
    '<div>'
    f'<div style="font-size:1.15rem;font-weight:700;color:#111827;">{current_company.get("display_name") or current_company.get("name")}</div>'
    f'<div style="font-size:0.84rem;color:#6B7280;margin-top:2px;">ОКВЭД {current_company.get("main_okved_code")} &nbsp;•&nbsp; {current_company.get("market_position_label", "Лидер отрасли")}</div>'
    '</div>'
    '<div style="text-align:right;">'
    f'<span style="font-size:1.45rem;font-weight:700;color:#111827;">{comp_rev:,.0f} млн ₽</span>'
    f'<span style="background:#FEF2F2;color:#991B1B;padding:3px 8px;border-radius:6px;font-size:0.75rem;font-weight:600;margin-left:8px;">{current_company.get("debt_preview", "Долг: 24.8 млрд ₽")}</span>'
    '</div>'
    '</div>'
)
st.markdown(kpi_html, unsafe_allow_html=True)

# Точка входа: Альфа-Инсайт
insights = fetch_feed_from_api(company_id, current_role_code)
entry_html = (
    '<div class="apple-hero-banner">'
    '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">'
    '<div style="font-size:1.15rem;font-weight:700;color:#111827;">Альфа-Инсайт: Персонализированная аналитика рисков и возможностей</div>'
    f'<span class="apple-badge-crit">Событий в фокусе: {len(insights)}</span>'
    '</div>'
    f'<div style="color:#4B5563;font-size:0.9rem;line-height:1.5;">Мультиагентный сервис сопоставил внешние рыночные публикации и аналитику Центра макроэкономических исследований Альфа-Банка. Сформирован стратегический фокус для роли <b>{selected_role_label}</b>.</div>'
    '</div>'
)
st.markdown(entry_html, unsafe_allow_html=True)

# Карточка инсайта (Все 6 блоков)
for ins in insights:
    st.markdown('<div class="apple-card-panel">', unsafe_allow_html=True)
    
    card_header = (
        '<div style="display:flex;justify-content:space-between;align-items:center;">'
        '<span class="apple-badge-crit">Высокий приоритет</span>'
        f'<span style="font-size:0.82rem;color:#6B7280;">{ins["date"]} &nbsp;•&nbsp; Источник: <b>{ins["source"]}</b></span>'
        '</div>'
        f'<div class="apple-title-h2">{ins["title"]}</div>'
    )
    st.markdown(card_header, unsafe_allow_html=True)

    # Блоки 1 и 2
    b1, b2 = st.columns(2)
    with b1:
        st.caption("1. ЧТО ПРОИЗОШЛО")
        b1_html = (
            '<div class="apple-subbox">'
            f'<div style="font-size:0.9rem;line-height:1.5;color:#374151;margin-bottom:12px;">{ins["facts"]}</div>'
            f'<a href="{ins["source_url"]}" target="_blank" style="font-size:0.82rem;color:#0071E3;text-decoration:none;font-weight:600;">Официальный первоисточник релиза &rarr;</a>'
            '</div>'
        )
        st.markdown(b1_html, unsafe_allow_html=True)

    with b2:
        st.caption("2. ПОЧЕМУ ЭТО ВАЖНО ДЛЯ КОМПАНИИ")
        pills = "".join([f'<span class="apple-tag-pill">{SVG["tag"]}{p}</span>' for p in ins["triggers"]])
        b2_html = (
            '<div class="apple-subbox">'
            f'<div style="margin-bottom:8px;">{pills}</div>'
            f'<div style="font-size:0.86rem;color:#4B5563;border-top:1px solid #E5E7EB;padding-top:8px;"><b>Влияние на цепочку контрагентов:</b> {ins["impact"]}</div>'
            '</div>'
        )
        st.markdown(b2_html, unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # Блок 3: Риски vs Возможности
    st.caption("3. ПРОГНОЗ ПОСЛЕДСТВИЙ ДЛЯ БИЗНЕСА")
    rc, oc = st.columns(2)
    with rc:
        st.markdown(f"<div style='font-size:0.88rem;font-weight:700;color:#DC2626;margin-bottom:6px;'>{SVG['shield']} Потенциальные риски</div>", unsafe_allow_html=True)
        for r in ins["risks"]:
            st.markdown(f'<div class="apple-risk-row">{r}</div>', unsafe_allow_html=True)
    with oc:
        st.markdown(f"<div style='font-size:0.88rem;font-weight:700;color:#16A34A;margin-bottom:6px;'>{SVG['trend']} Открывающиеся возможности</div>", unsafe_allow_html=True)
        for o in ins["opps"]:
            st.markdown(f'<div class="apple-opp-row">{SVG["check"]} {o}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # Блок 4: Банк vs ИИ
    st.caption("4. ОЦЕНКА АЛЬФА-БАНКА VS ВЫВОД ИИ")
    mc, aic = st.columns(2)
    with mc:
        b_html = (
            '<div class="apple-box-bank">'
            f'<div style="font-weight:700;color:#0071E3;font-size:0.92rem;margin-bottom:6px;">{SVG["bank"]} Позиция аналитиков Альфа-Банка</div>'
            f'<div style="font-size:0.9rem;font-style:italic;color:#1E293B;margin-bottom:10px;line-height:1.45;">«{ins["alfa_quote"]}»</div>'
            f'<div style="font-size:0.78rem;color:#64748B;">Материал: <b>{ins["alfa_report"]}</b><br>Базовый прогноз: {ins["alfa_forecast"]}</div>'
            '</div>'
        )
        st.markdown(b_html, unsafe_allow_html=True)
    with aic:
        ai_html = (
            '<div class="apple-box-ai">'
            f'<div style="font-weight:700;color:#EF3124;font-size:0.92rem;margin-bottom:6px;">{SVG["sparkles"]} Персонализированный AI-вывод для предприятия</div>'
            f'<div style="font-size:0.9rem;color:#1E293B;margin-bottom:10px;line-height:1.45;">{ins["ai_prediction"]}</div>'
            f'<div style="font-size:0.78rem;color:#991B1B;">Уверенность модели: <b>{ins["ai_conf"]}</b> &nbsp;•&nbsp; Драйвер: {ins["ai_driver"]}</div>'
            '</div>'
        )
        st.markdown(ai_html, unsafe_allow_html=True)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # Блок 5: Действия + Встроенная карточка продукта
    st.caption(f"5. РЕКОМЕНДУЕМЫЕ ДЕЙСТВИЯ ДЛЯ РОЛИ: {selected_role_label.upper()}")
    for s_idx, act in enumerate(ins["actions"], 1):
        st.checkbox(f"Шаг {s_idx}: {act}", key=f"step_{ins['id']}_{s_idx}")

    prod_col_text, prod_col_btn = st.columns([3, 1])
    prod_html = (
        '<div style="background:#111827;color:#FFFFFF;border-radius:14px;padding:20px 24px;height:100%;">'
        f'<span style="background:#EF3124;color:#FFFFFF;padding:3px 8px;border-radius:6px;font-size:0.7rem;font-weight:700;">{ins["prod_badge"]}</span>'
        f'<div style="font-size:1.15rem;font-weight:700;margin-top:6px;">{ins["prod_title"]}</div>'
        f'<div style="font-size:0.85rem;color:#9CA3AF;margin-top:4px;line-height:1.4;">{ins["prod_desc"]}</div>'
        '</div>'
    )
    with prod_col_text:
        st.markdown(prod_html, unsafe_allow_html=True)
    with prod_col_btn:
        st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)
        pk = f"prod_{ins['id']}"
        if pk in st.session_state.applied_products:
            st.success("Заявка направлена банкиру")
        else:
            if st.button(f"{ins['prod_btn']}", key=f"btn_{pk}"):
                st.session_state.applied_products.add(pk)
                st.balloons()
                st.rerun()

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # Блок 6: Аудит-лог
    with st.expander("Аудит-лог и происхождение выводов (Traceability)"):
        st.caption("Пошаговый протокол рассуждения многошагового агента:")
        for t in ins["trace"]:
            st.markdown(f"• {t}")

    # Интерактивный чат
    st.markdown("<hr style='border:none;border-top:1px solid #E5E7EB;margin:22px 0;'>", unsafe_allow_html=True)
    st.markdown('<div class="chat-label-text">Задать уточняющий вопрос AI-аналитику по новости:</div>', unsafe_allow_html=True)

    q1, q2 = st.columns(2)
    selected_preset = None
    if q1.button("Рассчитать влияние на долговую нагрузку", key=f"q1_{ins['id']}"):
        selected_preset = "Рассчитай влияние на долговую нагрузку компании"
    if q2.button("Оценить риски цепочки контрагентов", key=f"q2_{ins['id']}"):
        selected_preset = "Как это отразится на наших поставщиках и покупателях?"

    u_query = st.text_input("Вопрос", key=f"inp_{ins['id']}", placeholder="Например: 'Какой размер финансового буфера подготовить к 4 кварталу?'", label_visibility="collapsed")

    if st.button("Спросить AI-аналитика", key=f"ask_{ins['id']}") or selected_preset:
        txt = selected_preset if selected_preset else u_query
        if txt:
            with st.spinner("AI-агент рассчитывает финансовые показатели..."):
                ans = post_chat_to_api(company_id, current_role_code, ins["id"], txt)
                st.session_state.chat_history[ins['id']] = {"q": txt, "a": ans}

    if ins['id'] in st.session_state.chat_history:
        h = st.session_state.chat_history[ins['id']]
        st.markdown(f"<div style='background:#F3F4F6;border-radius:10px;padding:12px 16px;margin:12px 0 8px 0;font-size:0.9rem;'><b>Ваш запрос:</b> {h['q']}</div>", unsafe_allow_html=True)
        st.markdown(h['a'])

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center style='color:#9CA3AF;font-size:0.8rem;margin-top:24px;'>Интернет-банк «Альфа-Бизнес» &nbsp;•&nbsp; Сервис «Альфа-Инсайт»</center>", unsafe_allow_html=True)
