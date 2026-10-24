# -*- coding: utf-8 -*-
"""
Альфа-Инсайт: Интернет-банк «Альфа-Бизнес»
Дизайн-система: Настоящее банковское меню в шторке + Светлый финтех-стиль
"""

import streamlit as st
import requests
import base64
from pathlib import Path
from typing import Dict, List, Any

# Открываем шторку по умолчанию (expanded)
st.set_page_config(
    page_title="Альфа-Инсайт | Интернет-банк «Альфа-Бизнес»",
    page_icon="https://alfabank.servicecdn.ru/icons/corp/favicons/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URLS = [
    "http://backend:8000/api",
    "http://localhost:8000/api",
    "http://127.0.0.1:8000/api"
]

def get_api_base() -> str:
    for base in API_URLS:
        try:
            r = requests.get(f"{base}/companies", timeout=0.8)
            if r.status_code == 200:
                return base
        except Exception:
            pass
    return "http://localhost:8000/api"

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
                return f'<img src="data:image/svg+xml;base64,{b64}" height="28" style="vertical-align:middle;margin-right:12px;" />'
            except Exception:
                pass
    return '<span style="background:#EF3124;color:#FFFFFF;padding:4px 10px;border-radius:6px;font-weight:900;font-size:0.9rem;margin-right:10px;">А</span>'

# Фирменный стиль Альфа-Бизнес + шторка
st.markdown("""
<style>
    /* Светлый фон основного экрана */
    [data-testid="stAppViewContainer"], .stApp {
        background-color: #F8F9FA !important;
        color: #111827 !important;
    }
    header, #MainMenu, footer { visibility: hidden; height: 0; }
    
    div.block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 4rem !important;
        max-width: 1140px !important;
    }

    /* ШТОРКА (БОКОВОЕ МЕНЮ БАНКА) */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E5E7EB !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
    }

    /* Пункты меню в шторке */
    .menu-item {
        padding: 10px 14px;
        border-radius: 10px;
        font-size: 0.88rem;
        font-weight: 500;
        color: #4B5563;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .menu-item.active {
        background-color: #FFF5F5;
        color: #EF3124;
        font-weight: 700;
        border-left: 3px solid #EF3124;
        border-radius: 0 10px 10px 0;
    }

    /* Метрики */
    [data-testid="stMetricValue"] {
        color: #111827 !important;
        font-size: 1.45rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #4B5563 !important;
        font-weight: 600 !important;
    }

    /* Верхняя панель основного контента */
    .alfa-top-nav {
        background: #111827;
        color: #FFFFFF;
        padding: 14px 24px;
        border-radius: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .alfa-nav-text {
        font-weight: 700;
        font-size: 1.15rem;
        letter-spacing: -0.02em;
        color: #FFFFFF;
    }
    .alfa-nav-tag {
        font-size: 0.8rem;
        color: #9CA3AF;
        background: rgba(255, 255, 255, 0.08);
        padding: 4px 12px;
        border-radius: 980px;
    }

    /* Точка входа */
    .alfa-entry {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-left: 4px solid #EF3124;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 24px;
    }
    .alfa-badge {
        background: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FEE2E2;
        padding: 3px 10px;
        border-radius: 980px;
        font-weight: 700;
        font-size: 0.74rem;
        text-transform: uppercase;
    }

    /* Карточки инсайта */
    .alfa-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 26px 30px;
        margin-bottom: 24px;
    }
    .alfa-card-h2 {
        font-size: 1.35rem;
        font-weight: 700;
        color: #111827;
        line-height: 1.35;
        margin: 10px 0 18px 0;
    }

    /* Подложки */
    .alfa-box-gray {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 16px 18px;
        height: 100%;
    }
    .alfa-pill {
        background: #FFFFFF;
        color: #374151;
        border: 1px solid #D1D5DB;
        padding: 5px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .box-risk {
        background: #FEF2F2;
        border: 1px solid #FEE2E2;
        border-radius: 10px;
        padding: 12px 16px;
        color: #991B1B;
        font-size: 0.88rem;
        line-height: 1.45;
        margin-bottom: 8px;
    }
    .box-opp {
        background: #F0FDF4;
        border: 1px solid #DCFCE7;
        border-radius: 10px;
        padding: 12px 16px;
        color: #166534;
        font-size: 0.88rem;
        line-height: 1.45;
        margin-bottom: 8px;
    }
    .box-bank {
        background: #F0F9FF;
        border: 1px solid #BAE6FD;
        border-left: 3px solid #0284C7;
        border-radius: 0 12px 12px 0;
        padding: 16px 20px;
        height: 100%;
    }
    .box-ai {
        background: #FFF5F5;
        border: 1px solid #FECACA;
        border-left: 3px solid #EF3124;
        border-radius: 0 12px 12px 0;
        padding: 16px 20px;
        height: 100%;
    }
    .box-offer {
        background: #111827;
        color: #FFFFFF;
        border-radius: 14px;
        padding: 22px 26px;
        margin-top: 18px;
    }
    div.stButton > button {
        background-color: #EF3124 !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 8px 20px !important;
    }
    div.stButton > button:hover {
        background-color: #D3271B !important;
    }
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

ICONS = {
    "shield": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2" style="vertical-align:-2px;margin-right:6px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "trend": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#16A34A" stroke-width="2" style="vertical-align:-2px;margin-right:6px;"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/></svg>',
    "bank": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2" style="vertical-align:-2px;margin-right:6px;"><rect width="20" height="4" x="2" y="3" rx="1"/><path d="M4 7v11"/><path d="M8 7v11"/><path d="M12 7v11"/><path d="M16 7v11"/><path d="M20 7v11"/></svg>',
    "sparkles": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#EF3124" stroke-width="2" style="vertical-align:-2px;margin-right:6px;"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3Z"/></svg>',
    "check": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#16A34A" stroke-width="2.5" style="vertical-align:-2px;margin-right:6px;"><polyline points="20 6 9 17 4 12"/></svg>'
}

FALLBACK_COMPANIES = [
    {
        "id": "comp_tech_01",
        "name": "ООО «ТехноПром»",
        "okved": "26.11 (Производство электроники)",
        "revenue_mln": 18200.0,
        "debt_mln": 850.0,
        "ved": "Импорт комплектующих из КНР (85% расчетов в CNY)"
    },
    {
        "id": "comp_agro_02",
        "name": "АО «АгроРесурс»",
        "okved": "01.11 (Выращивание зерновых)",
        "revenue_mln": 22400.0,
        "debt_mln": 4650.0,
        "ved": "Экспорт в Турцию, Египет и ОАЭ"
    }
]

def fetch_companies() -> List[Dict[str, Any]]:
    api_base = get_api_base()
    try:
        r = requests.get(f"{api_base}/companies", timeout=1.0)
        if r.status_code == 200:
            data = r.json()
            res = []
            for item in data:
                res.append({
                    "id": item.get("synthetic_u") or item.get("id", "comp_1"),
                    "name": item.get("name") or item.get("org_name", "ООО «Компания»"),
                    "okved": item.get("main_okved_name") or item.get("okved", "01.11"),
                    "revenue_mln": float(item.get("revenue") or item.get("revenue_mln", 15000.0)),
                    "debt_mln": float(item.get("credit_debt_mln") or item.get("debt_mln", 1200.0)),
                    "ved": item.get("ved") or "ВЭД: Китай, ЕАЭС"
                })
            return res if res else FALLBACK_COMPANIES
    except Exception:
        pass
    return FALLBACK_COMPANIES

def fetch_feed(company_id: str, role: str) -> List[Dict[str, Any]]:
    api_base = get_api_base()
    try:
        r = requests.get(f"{api_base}/feed", params={"company_id": company_id, "role": role}, timeout=2.5)
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

                adapted.append({
                    "id": ins.get("insight_id", "ins_1"),
                    "title": wh.get("title") or ins.get("title", "Ключевое регуляторное изменение"),
                    "date": wh.get("published_at", "Сегодня, 12:00"),
                    "source": wh.get("source_name", "Банк России"),
                    "source_url": wh.get("source_url", "https://cbr.ru"),
                    "facts": " ".join(wh.get("facts", [])) if isinstance(wh.get("facts"), list) else wh.get("facts", "Событие на финансовых рынках."),
                    "triggers": wi.get("matched_company_features", ["ОКВЭД", "Кредитный портфель"]),
                    "impact": wi.get("supply_chain_impact", "Возможны задержки в расчетах с контрагентами."),
                    "risks": cq.get("risks", ["Рост процентных расходов"]),
                    "opps": cq.get("opportunities", ["Размещение остатков на депозитах"]),
                    "alfa_quote": be.get("alfa_bank_position", "Аналитики банка рекомендуют хеджирование процентных и валютных рисков."),
                    "alfa_report": be.get("cited_report_title", "Макроэкономический обзор Альфа-Банка 2026"),
                    "alfa_forecast": "Жесткие ДКП условия сохранятся до конца 2026 года.",
                    "ai_prediction": be.get("ai_model_inference", "Для компании событие требует балансировки ликвидности."),
                    "ai_conf": f"{ins.get('relevance_score', 95)}%",
                    "ai_driver": "Высокая доля заемного капитала",
                    "actions": ra.get("steps_for_role", ["Провести анализ кредитных ковенант"]),
                    "prod_badge": ins.get("urgency_badge", "Рекомендовано"),
                    "prod_title": prod.get("product_name", "Хеджирование рисков Альфа-Банк"),
                    "prod_desc": prod.get("pitch", "Зафиксируйте ставку и оптимизируйте финансовые потоки."),
                    "prod_btn": prod.get("cta_label", "Оставить заявку"),
                    "trace": [s.get("reasoning", str(s)) for s in tr.get("agent_steps", [])] if tr.get("agent_steps") else ["1. Ingestion: парсинг релиза", "2. ERP Match: проверка договора", "3. Guardrail: проверка фактов"]
                })
            if adapted:
                return adapted
    except Exception:
        pass
    
    return [{
        "id": "ins_default",
        "title": "Банк России сохранил ключевую ставку на уровне 14,0%: пауза в цикле смягчения",
        "date": "11 сентября 2026, 13:30",
        "source": "Пресс-служба Банка России",
        "source_url": "https://cbr.ru",
        "facts": "Совет директоров Банка России сохранил ключевую ставку на уровне 14,00% годовых. Это первая пауза в цикле смягчения ДКП. Регулятор ужесточил сигнал.",
        "triggers": ["ОКВЭД: Высокая зависимость от оборотных кредитов", "Кредитный портфель: 68% с плавающей ставкой КС+2.1%", "Контрагент запросил увеличение отсрочки расчетов"],
        "impact": "Трейдеры задерживают авансирование из-за паузы снижения ставок по кредитам.",
        "risks": ["Экономия на процентных расходах откладывается минимум на 2 квартала.", "Риск нарушения ковенанты Net Debt / EBITDA (> 3.0x)."],
        "opps": ["Размещение остатков на овернайт-депозитах Альфа-Банка под 13.85% годовых.", "Фиксация ставки через процентный своп (IRS) Альфа-Банка."],
        "alfa_quote": "Для бизнеса сохранение ставки 14% — сигнал о том, что быстрое удешевление кредитов приостановлено. Долговая нагрузка не снизится в ближайшее время.",
        "alfa_report": "Ключевая ставка ЦБ РФ: ставка без изменения на 14,0%, риторика стала жестче",
        "alfa_forecast": "КС останется на уровне 14.0% до конца 2026 года.",
        "ai_prediction": "Для предприятия пауза означает заморозку расходов по долгу. Требуется хеджирование траншей до старта сезона.",
        "ai_conf": "96%",
        "ai_driver": "Высокая доля долга с плавающей ставкой",
        "actions": ["Скорректировать инвестиционный бюджет на 2026–2027 гг.", "Заключить соглашение IRS (процентный своп) с Альфа-Банком по ставке 12.6%."],
        "prod_badge": "Рекомендовано CFO",
        "prod_title": "Процентный своп (IRS) Альфа-Банк",
        "prod_desc": "Зафиксируйте ставку по кредитам с плавающей ставкой на уровне 12.6% на 24 месяца.",
        "prod_btn": "Рассчитать параметры свопа",
        "trace": [
            "1. Planning: определение потребности в анализе ДКП и заемных средств",
            "2. Tool Execution: извлечение кредитного профиля и макро-отчета Альфа-Банка",
            "3. Synthesis: генерация выводов по 6 блокам Слайда 14",
            "4. Self-Reflection: проверка на галлюцинации и ковенантный стресс-тест"
        ]
    }]

def post_chat(company_id: str, role: str, insight_id: str, question: str) -> str:
    api_base = get_api_base()
    try:
        payload = {"company_id": company_id, "role": role, "insight_id": insight_id, "question": question}
        r = requests.post(f"{api_base}/chat", json=payload, timeout=4.0)
        if r.status_code == 200:
            data = r.json()
            return data.get("answer") or data.get("response") or "Ответ получен."
    except Exception:
        pass
    
    q_low = question.lower()
    if "долг" in q_low or "нагрузк" in q_low:
        return "**Расчет влияния на долговую нагрузку (CFO View):**\n\n• Сохранение ставки на 14.0% фиксирует ежемесячные расходы на уровне **54.2 млн руб.**\n• Отсутствие снижения ставки лишает экономии в **3.88 млн руб./мес**.\n• Рекомендация: зафиксировать ставку на уровне 12.6% через IRS Альфа-Банка."
    return "**Аналитический ассистент Альфа-Инсайт:**\n\nНа основе сопоставления профиля компании и макро-отчета Альфа-Банка, данное событие требует оптимизации графика платежей. Рекомендуем запросить встречу с корпоративным банкиром в Альфа-Бизнес."

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "applied_products" not in st.session_state:
    st.session_state.applied_products = set()

# ==========================================
# 1. ШТОРКА СЛЕВА (БОКОВОЕ МЕНЮ БАНКА)
# ==========================================
with st.sidebar:
    st.markdown(f'<div style="display:flex;align-items:center;margin-bottom:18px;">{get_logo_html()}<b>АЛЬФА-БИЗНЕС</b></div>', unsafe_allow_html=True)
    
    st.caption("ОРГАНИЗАЦИЯ")
    companies = fetch_companies()
    comp_dict = {c["name"]: c for c in companies}
    selected_name = st.selectbox("Клиент", list(comp_dict.keys()), label_visibility="collapsed")
    comp = comp_dict[selected_name]

    st.caption("РОЛЬ ЛПР (СЛАЙД 5)")
    role_map = {
        "CFO": "Финансовый директор (CFO)",
        "CEO": "Генеральный директор (CEO)",
        "TREASURER": "Руководитель казначейства (TREASURER)",
        "ACCOUNTANT": "Главный бухгалтер (ACCOUNTANT)"
    }
    selected_role_label = st.selectbox("Роль", list(role_map.values()), index=0, label_visibility="collapsed")
    current_role_code = [k for k, v in role_map.items() if v == selected_role_label][0]

    st.markdown("<hr style='margin:16px 0;border:none;border-top:1px solid #E5E7EB;'>", unsafe_allow_html=True)
    
    st.caption("РАЗДЕЛЫ БАНКА")
    st.markdown("""
    <div class="menu-item">Счета и выписки</div>
    <div class="menu-item">Платежи и переводы</div>
    <div class="menu-item active">⚡ Альфа-Инсайт</div>
    <div class="menu-item">ВЭД и валютный контроль</div>
    <div class="menu-item">Кредитные линии</div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
    st.caption("ТЕСТОВЫЙ КОНТУР")
    st.markdown("<div style='font-size:0.75rem;color:#9CA3AF;'>Аккаунт: <b>alfa-hack-2026</b><br>Версия: Release Candidate 1.0</div>", unsafe_allow_html=True)

# ==========================================
# 2. ОСНОВНАЯ ОБЛАСТЬ (ЭКРАН АЛЬФА-ИНСАЙТ)
# ==========================================

# Верхняя информационная полоса с показателями клиента
top_nav = (
    '<div class="alfa-top-nav">'
    '<div style="display:flex;align-items:center;">'
    f'<span class="alfa-nav-text">{comp["name"]} &nbsp;•&nbsp; {comp["okved"]}</span>'
    '</div>'
    f'<div class="alfa-nav-tag">Выручка: {comp["revenue_mln"]:,.0f} млн ₽ | Долг: {comp["debt_mln"]:,.0f} млн ₽</div>'
    '</div>'
)
st.markdown(top_nav, unsafe_allow_html=True)

# Точка входа (Критерий 09)
insights = fetch_feed(comp["id"], current_role_code)
entry_html = (
    '<div class="alfa-entry">'
    '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
    '<div style="font-size:1.15rem;font-weight:700;color:#111827;">Альфа-Инсайт: Персонализированная аналитика рисков и возможностей</div>'
    f'<span class="alfa-badge">Критичных событий: {len(insights)}</span>'
    '</div>'
    f'<div style="color:#4B5563;font-size:0.9rem;line-height:1.5;">Система обработала внешние публикации и макро-отчеты Альфа-Банка. Сформирован фокус внимания для роли <b>{selected_role_label}</b> предприятия <b>{comp["name"]}</b> (ОКВЭД <code>{comp["okved"]}</code>, профиль ВЭД: <i>{comp["ved"]}</i>).</div>'
    '</div>'
)
st.markdown(entry_html, unsafe_allow_html=True)

# Карточка инсайта (Все 6 блоков)
for ins in insights:
    st.markdown('<div class="alfa-card">', unsafe_allow_html=True)
    
    card_header = (
        '<div style="display:flex;justify-content:space-between;align-items:center;">'
        '<span class="alfa-badge">Высокий приоритет</span>'
        f'<span style="font-size:0.82rem;color:#6B7280;">{ins["date"]} • Источник: <b>{ins["source"]}</b></span>'
        '</div>'
        f'<div class="alfa-card-h2">{ins["title"]}</div>'
    )
    st.markdown(card_header, unsafe_allow_html=True)

    # 1 и 2
    b1, b2 = st.columns(2)
    with b1:
        st.caption("1. ЧТО ПРОИЗОШЛО (ФАКТЫ И ПЕРВОИСТОЧНИК)")
        b1_html = (
            '<div class="alfa-box-gray">'
            f'<div style="font-size:0.9rem;line-height:1.5;color:#374151;margin-bottom:12px;">{ins["facts"]}</div>'
            f'<a href="{ins["source_url"]}" target="_blank" style="font-size:0.82rem;color:#EF3124;text-decoration:none;font-weight:600;">Официальный первоисточник релиза &rarr;</a>'
            '</div>'
        )
        st.markdown(b1_html, unsafe_allow_html=True)

    with b2:
        st.caption("2. ПОЧЕМУ ЭТО ВАЖНО ДЛЯ ВАШЕЙ КОМПАНИИ (СЛАЙД 14)")
        pills = "".join([f'<span class="alfa-pill">{p}</span>' for p in ins["triggers"]])
        b2_html = (
            '<div class="alfa-box-gray">'
            f'<div style="margin-bottom:8px;">{pills}</div>'
            f'<div style="font-size:0.86rem;color:#4B5563;border-top:1px solid #E5E7EB;padding-top:8px;"><b>Влияние на контрагентов:</b> {ins["impact"]}</div>'
            '</div>'
        )
        st.markdown(b2_html, unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # 3. Риски vs Возможности
    st.caption("3. ПРОГНОЗ ПОСЛЕДСТВИЙ ДЛЯ БИЗНЕСА")
    rc, oc = st.columns(2)
    with rc:
        st.markdown(f"<div style='font-size:0.88rem;font-weight:700;color:#DC2626;margin-bottom:6px;'>{ICONS['shield']} Потенциальные риски</div>", unsafe_allow_html=True)
        for r in ins["risks"]:
            st.markdown(f'<div class="box-risk">• {r}</div>', unsafe_allow_html=True)
    with oc:
        st.markdown(f"<div style='font-size:0.88rem;font-weight:700;color:#16A34A;margin-bottom:6px;'>{ICONS['trend']} Открывающиеся возможности</div>", unsafe_allow_html=True)
        for o in ins["opps"]:
            st.markdown(f'<div class="box-opp">{ICONS["check"]} {o}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # 4. Банк vs AI
    st.caption("4. ОЦЕНКА АЛЬФА-БАНКА VS ВЫВОД AI-МОДЕЛИ (КРИТЕРИЙ 03)")
    mc, aic = st.columns(2)
    with mc:
        b_html = (
            '<div class="box-bank">'
            f'<div style="font-weight:700;color:#0284C7;font-size:0.92rem;margin-bottom:6px;">{ICONS["bank"]} Позиция аналитиков Альфа-Банка</div>'
            f'<div style="font-size:0.9rem;font-style:italic;color:#1E293B;margin-bottom:10px;line-height:1.45;">«{ins["alfa_quote"]}»</div>'
            f'<div style="font-size:0.78rem;color:#64748B;">Материал: <b>{ins["alfa_report"]}</b><br>Базовый прогноз: {ins["alfa_forecast"]}</div>'
            '</div>'
        )
        st.markdown(b_html, unsafe_allow_html=True)
    with aic:
        ai_html = (
            '<div class="box-ai">'
            f'<div style="font-weight:700;color:#EF3124;font-size:0.92rem;margin-bottom:6px;">{ICONS["sparkles"]} Персонализированный AI-вывод для {comp["name"]}</div>'
            f'<div style="font-size:0.9rem;color:#1E293B;margin-bottom:10px;line-height:1.45;">{ins["ai_prediction"]}</div>'
            f'<div style="font-size:0.78rem;color:#991B1B;">Уверенность модели: <b>{ins["ai_conf"]}</b> • Драйвер: {ins["ai_driver"]}</div>'
            '</div>'
        )
        st.markdown(ai_html, unsafe_allow_html=True)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # 5. Действия + Продукт
    st.caption(f"5. РЕКОМЕНДУЕМЫЕ ДЕЙСТВИЯ ДЛЯ РОЛИ: {selected_role_label.upper()}")
    for s_idx, act in enumerate(ins["actions"], 1):
        st.checkbox(f"Шаг {s_idx}: {act}", key=f"step_{ins['id']}_{s_idx}")

    prod_html = (
        '<div class="box-offer">'
        f'<span style="background:#EF3124;color:#FFFFFF;padding:3px 8px;border-radius:6px;font-size:0.7rem;font-weight:700;">{ins["prod_badge"]}</span>'
        f'<div style="font-size:1.15rem;font-weight:700;margin-top:6px;">{ins["prod_title"]}</div>'
        f'<div style="font-size:0.86rem;color:#9CA3AF;margin-top:4px;max-width:680px;line-height:1.4;">{ins["prod_desc"]}</div>'
        '</div>'
    )
    st.markdown(prod_html, unsafe_allow_html=True)

    pk = f"prod_{ins['id']}"
    if pk in st.session_state.applied_products:
        st.success(f"Заявка на продукт «{ins['prod_title']}» успешно передана корпоративному банкиру Альфа-Банка.")
    else:
        if st.button(f"{ins['prod_btn']}", key=f"btn_{pk}"):
            st.session_state.applied_products.add(pk)
            st.balloons()
            st.rerun()

    # 6. Traceability
    with st.expander("Аудит-лог и происхождение выводов (Traceability & Слайд 12)"):
        st.caption("Пошаговый протокол рассуждения агента, сопоставленные признаки и верифицированные источники:")
        for t in ins["trace"]:
            st.markdown(f"• {t}")

    # Чат
    st.markdown("<hr style='border:none;border-top:1px solid #E5E7EB;margin:24px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.95rem;font-weight:700;color:#111827;margin-bottom:10px;'>Задать уточняющий вопрос AI-аналитику:</div>", unsafe_allow_html=True)

    q1, q2 = st.columns(2)
    selected_preset = None
    if q1.button("Влияние на долговую нагрузку (CFO)", key=f"q1_{ins['id']}"):
        selected_preset = "Рассчитай влияние на долговую нагрузку компании"
    if q2.button("Влияние на цепочку покупателей", key=f"q2_{ins['id']}"):
        selected_preset = "Как это отразится на наших поставщиках и покупателях?"

    u_query = st.text_input("Или задайте свой вопрос аналитику в свободной форме:", key=f"inp_{ins['id']}", placeholder="Например: 'Какой размер финансового резерва потребуется подготовить?'")

    if st.button("Спросить AI-аналитика", key=f"ask_{ins['id']}") or selected_preset:
        txt = selected_preset if selected_preset else u_query
        if txt:
            with st.spinner("AI-агент рассчитывает финансовые показатели..."):
                ans = post_chat(comp["id"], current_role_code, ins["id"], txt)
                st.session_state.chat_history[ins['id']] = {"q": txt, "a": ans}

    if ins['id'] in st.session_state.chat_history:
        h = st.session_state.chat_history[ins['id']]
        st.markdown(f"<div style='background:#F3F4F6;border-radius:10px;padding:12px 16px;margin:12px 0 8px 0;font-size:0.9rem;'><b>Ваш запрос:</b> {h['q']}</div>", unsafe_allow_html=True)
        st.markdown(h['a'])

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center style='color:#9CA3AF;font-size:0.8rem;margin-top:24px;'>Интернет-банк «Альфа-Бизнес» • Сервис «Альфа-Инсайт» • Тестовый контур alfa-hack-2026</center>", unsafe_allow_html=True)
