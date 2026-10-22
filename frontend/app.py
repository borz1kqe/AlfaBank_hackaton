# frontend/app.py
import os
import base64
from pathlib import Path
import requests
import streamlit as st

from mock_data import (
    COMPANIES,
    ROLES,
    get_personalized_feed,
    generate_mock_chat_answer,
    analyze_custom_news_Realtime,
)

st.set_page_config(
    page_title="Альфа-Бизнес — Аналитика",
    page_icon="alfa-bank.svg" if Path("alfa-bank.svg").exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BASE_DIR = Path(__file__).parent


def load_svg_base64(filename: str) -> str:
    for candidate in [BASE_DIR / filename, BASE_DIR / "logos" / filename]:
        if candidate.exists():
            data = candidate.read_bytes()
            return f"data:image/svg+xml;base64,{base64.b64encode(data).decode('utf-8')}"
    return ""


ALFA_LOGO_B64 = load_svg_base64("alfa-bank.svg")
ALFA_BIZ_LOGO_B64 = load_svg_base64("alfa-bank-business.svg")

if "selected_company_id" not in st.session_state:
    st.session_state.selected_company_id = COMPANIES[0]["company_id"]
if "selected_role" not in st.session_state:
    st.session_state.selected_role = "CFO"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "custom_insights" not in st.session_state:
    st.session_state.custom_insights = []


def api_get_companies():
    try:
        resp = requests.get(f"{BACKEND_URL}/api/companies", timeout=1.0)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                return data
    except Exception:
        pass
    return COMPANIES


def api_get_feed(company_id: str, role: str):
    try:
        resp = requests.get(
            f"{BACKEND_URL}/api/feed",
            params={"company_id": company_id, "role": role},
            timeout=1.8,
        )
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                return data
    except Exception:
        pass
    return get_personalized_feed(company_id, role)


def api_post_chat(company_id: str, role: str, insight_id: str, question: str):
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/chat",
            json={
                "company_id": company_id,
                "role": role,
                "insight_id": insight_id,
                "question": question,
            },
            timeout=3.0,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return generate_mock_chat_answer(company_id, role, insight_id, question)


st.markdown(
    """
<style>
    :root {
        --font-sf: system-ui, -apple-system, BlinkMacSystemFont, ui-sans-serif, sans-serif;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    .stDeployButton, [data-testid="stAppDeployButton"], #MainMenu {
        display: none !important;
    }
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"] {
        visibility: visible !important;
        display: flex !important;
    }

    html, body, .stApp, div:not([data-testid="stIconMaterial"]), p, h1, h2, h3, h4, label, button, input, textarea, li, blockquote, svg text {
        font-family: var(--font-sf) !important;
        -webkit-font-smoothing: antialiased !important;
        letter-spacing: -0.016em;
    }
    span:not([data-testid="stIconMaterial"]):not(.material-symbols-rounded) {
        font-family: var(--font-sf) !important;
        letter-spacing: -0.016em;
    }
    [data-testid="stIconMaterial"], .material-symbols-rounded {
        font-family: "Material Symbols Rounded" !important;
    }

    /* Спокойный архитектурный фон без "ИИ-свечений" */
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    section.main {
        background-color: #E6E9EF !important;
        color: #11141A;
    }

    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 4rem !important;
        padding-left: 2.4rem !important;
        padding-right: 2.4rem !important;
        max-width: 1440px !important;
    }

    /* Левая шторка: матовое темное стекло */
    section[data-testid="stSidebar"] {
        background: rgba(17, 19, 24, 0.94) !important;
        backdrop-filter: blur(28px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(180%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span:not([data-testid="stIconMaterial"]),
    section[data-testid="stSidebar"] label {
        color: #F1F5F9 !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }

    .sidebar-glass-box {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 12px;
    }
    .sidebar-row {
        display: flex;
        justify-content: space-between;
        padding: 5px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        font-size: 12px;
    }
    .sidebar-row:last-child {
        border-bottom: none;
        padding-bottom: 0;
    }

    /* Селекты рабочей области */
    div[data-baseweb="select"] > div {
        background: #F4F6F9 !important;
        color: #11141A !important;
        border: 1px solid #CFD6E2 !important;
        border-radius: 10px !important;
        min-height: 40px !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03) !important;
    }
    div[data-baseweb="select"] span {
        color: #11141A !important;
    }

    /* Капсульные вкладки без красной черты */
    [role="tablist"] {
        background: #D9DFE8 !important;
        padding: 4px !important;
        border-radius: 11px !important;
        gap: 4px !important;
        width: fit-content !important;
        margin-bottom: 12px !important;
        border: 1px solid #CBD2DE !important;
    }
    [role="tablist"]::before, [role="tablist"]::after {
        display: none !important;
    }
    button[role="tab"] {
        background: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        height: 32px !important;
    }
    button[role="tab"] p, button[role="tab"] span, button[role="tab"] div {
        font-size: 12.5px !important;
        font-weight: 600 !important;
        color: #475569 !important;
    }
    button[role="tab"][aria-selected="true"] {
        background: #F4F6F9 !important;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.08) !important;
    }
    button[role="tab"][aria-selected="true"] p,
    button[role="tab"][aria-selected="true"] span,
    button[role="tab"][aria-selected="true"] div {
        color: #11141A !important;
        font-weight: 700 !important;
    }
    div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {
        display: none !important;
        height: 0 !important;
    }

    /* Верхний бар */
    .topbar {
        background: #111318;
        color: #FFFFFF;
        padding: 16px 24px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
    }

    /* Строгая банковская полоса ключевых показателей (4 карточки) */
    .kpi-strip {
        display: grid;
        grid-template-columns: repeat(3, 1fr) 1.55fr;
        gap: 14px;
        align-items: stretch;
        margin-bottom: 16px;
    }
    .kpi-card {
        background: #F4F6F9;
        border: 1px solid #CFD6E2;
        border-radius: 14px;
        padding: 16px 18px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .kpi-val {
        font-size: 23px;
        font-weight: 700;
        color: #11141A;
        letter-spacing: -0.6px;
        margin: 6px 0 2px 0;
        font-variant-numeric: tabular-nums;
    }
    .kpi-sub {
        font-size: 12px;
        color: #475569;
    }
    .kpi-foot {
        font-size: 11.5px;
        color: #475569;
        padding-top: 10px;
        margin-top: 10px;
        border-top: 1px solid #E2E6EE;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .kpi-radar {
        background: #16181F;
        color: #FFFFFF;
        border-radius: 14px;
        padding: 16px 20px;
        border-left: 4px solid #EF3124;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Единый строгий лист отчета (Editorial Sheet — как в Stripe / Linear, 0 "ИИ-пузырей") */
    .report-sheet {
        background: #F4F6F9;
        border: 1px solid #CFD6E2;
        border-radius: 16px;
        margin-bottom: 14px;
        overflow: hidden;
    }
    .sheet-head {
        padding: 18px 22px;
        border-bottom: 1px solid #DEE3EC;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 16px;
    }
    .sheet-grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        border-bottom: 1px solid #DEE3EC;
    }
    .sheet-cell {
        padding: 18px 22px;
        border-right: 1px solid #DEE3EC;
    }
    .sheet-cell:last-child {
        border-right: none;
    }
    .cell-kicker {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748B;
        margin-bottom: 8px;
    }
    .tag-minimal {
        display: inline-block;
        background: #E6EAF0;
        color: #1E293B;
        border: 1px solid #CBD2DE;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 11.5px;
        font-weight: 500;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    .tag-accent {
        display: inline-block;
        background: rgba(239, 49, 36, 0.10);
        color: #B91C1C;
        border: 1px solid rgba(239, 49, 36, 0.25);
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 11.5px;
        font-weight: 600;
        margin-right: 5px;
        margin-bottom: 5px;
    }

    div.stButton > button[kind="primary"] {
        background: #EF3124 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 0.5rem 1rem !important;
    }
    div.stButton > button[kind="secondary"] {
        background: #E6EAF0 !important;
        color: #11141A !important;
        border: 1px solid #CBD2DE !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        font-size: 12.5px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

companies_list = api_get_companies()
company_map = {c["company_id"]: c for c in companies_list}

# --- САЙДБАР ---
with st.sidebar:
    if ALFA_BIZ_LOGO_B64:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;padding:4px 0 16px 0;border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:16px;">'
            f'<div style="width:38px;height:38px;border-radius:10px;overflow:hidden;flex-shrink:0;"><img src="{ALFA_BIZ_LOGO_B64}" style="width:100%;height:100%;object-fit:cover;display:block;"/></div>'
            f'<div><div style="font-weight:700;font-size:15px;color:#FFFFFF;">Альфа-Бизнес</div>'
            f'<div style="font-size:11.5px;color:#94A3B8;">Крупный бизнес • CIB</div></div></div>',
            unsafe_allow_html=True,
        )

    nav_mode = st.radio(
        "Навигация",
        options=[
            "Аналитическая лента",
            "Разбор внешнего материала",
            "Метрики и безопасность",
        ],
        label_visibility="collapsed",
    )

    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
    selected_comp_id = st.selectbox(
        "Организация",
        options=list(company_map.keys()),
        format_func=lambda cid: company_map[cid]["name"],
        index=list(company_map.keys()).index(st.session_state.selected_company_id),
    )
    st.session_state.selected_company_id = selected_comp_id

    selected_role_key = st.selectbox(
        "Роль руководителя",
        options=list(ROLES.keys()),
        format_func=lambda r: ROLES[r],
        index=list(ROLES.keys()).index(st.session_state.selected_role),
    )
    st.session_state.selected_role = selected_role_key

    current_company = company_map[selected_comp_id]

    st.markdown(
        """
        <div style="font-size:10.5px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.5px;margin:16px 0 6px 2px;">Индикаторы рынка</div>
        <div class="sidebar-glass-box">
            <div class="sidebar-row"><span style="color:#94A3B8;">Ключевая ставка ЦБ</span><span style="font-weight:600;color:#F8FAFC;">14,00%</span></div>
            <div class="sidebar-row"><span style="color:#94A3B8;">RUONIA</span><span style="font-weight:600;color:#F8FAFC;">13,85%</span></div>
            <div class="sidebar-row"><span style="color:#94A3B8;">CNY / RUB</span><span style="font-weight:600;color:#F8FAFC;">12,84 ₽</span></div>
            <div class="sidebar-row"><span style="color:#94A3B8;">ОФЗ 2Y</span><span style="font-weight:600;color:#F8FAFC;">14,65%</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- ВЕРХНИЙ БАР ---
logo_html = (
    f'<div style="width:38px;height:38px;border-radius:10px;overflow:hidden;flex-shrink:0;"><img src="{ALFA_LOGO_B64}" style="width:100%;height:100%;object-fit:cover;display:block;"/></div>'
    if ALFA_LOGO_B64
    else '<div style="width:38px;height:38px;border-radius:10px;background:#EF3124;color:#FFF;display:flex;align-items:center;justify-content:center;font-weight:800;">A</div>'
)

st.markdown(
    f"""
<div class="topbar">
    <div style="display:flex;align-items:center;gap:14px;">
        {logo_html}
        <div>
            <div style="font-size:17px;font-weight:700;color:#FFFFFF;letter-spacing:-0.2px;">Альфа-Инсайт</div>
            <div style="font-size:12.5px;color:#94A3B8;">{current_company['name']} • {current_company['okved_name']} • {ROLES[selected_role_key]}</div>
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
        <span style="background:rgba(239,49,36,0.18);border:1px solid rgba(239,49,36,0.45);color:#FCA5A5;padding:5px 12px;border-radius:999px;font-size:12px;font-weight:600;">
            2 события требуют внимания
        </span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# --- ПЕРЕКЛЮЧАТЕЛЬ КОНТЕКСТА ---
c1, c2, c3 = st.columns([2.2, 1.8, 1.0])
with c1:
    top_comp = st.selectbox(
        "Юридическое лицо",
        options=list(company_map.keys()),
        format_func=lambda cid: f"{company_map[cid]['name']} ({company_map[cid]['revenue_Text']})",
        index=list(company_map.keys()).index(st.session_state.selected_company_id),
        key="top_comp_select",
    )
    if top_comp != st.session_state.selected_company_id:
        st.session_state.selected_company_id = top_comp
        st.rerun()
with c2:
    top_role = st.selectbox(
        "Роль руководителя",
        options=list(ROLES.keys()),
        format_func=lambda r: ROLES[r],
        index=list(ROLES.keys()).index(st.session_state.selected_role),
        key="top_role_select",
    )
    if top_role != st.session_state.selected_role:
        st.session_state.selected_role = top_role
        st.rerun()
with c3:
    st.markdown('<div style="height:27px;"></div>', unsafe_allow_html=True)
    filter_crit = st.checkbox("Высокий приоритет", value=False)

current_company = company_map[st.session_state.selected_company_id]
current_role = st.session_state.selected_role

# --- ПОЛОСА KPI СЧЕТОВ И ТОЧКИ ВХОДА ---
credit_val = current_company["accounts_summary"].get("active_credit_line", "")
credit_sub = current_company["accounts_summary"].get("credit_sub", "")

st.markdown(
    f"""
<div class="kpi-strip">
    <div class="kpi-card">
        <div>
            <div class="kpi-label">Расчетный счет RUB</div>
            <div class="kpi-val">{current_company['accounts_summary']['ruble_balance']}</div>
            <div class="kpi-sub">Рублевая ликвидность</div>
        </div>
        <div class="kpi-foot">
            <span>Статус счета</span>
            <span style="color:#059669;font-weight:600;">Активен</span>
        </div>
    </div>
    <div class="kpi-card">
        <div>
            <div class="kpi-label">Валютный счет CNY</div>
            <div class="kpi-val">{current_company['accounts_summary']['cny_balance']}</div>
            <div class="kpi-sub">ВЭД: {current_company['fts_country']}</div>
        </div>
        <div class="kpi-foot">
            <span>Прямой клиринг</span>
            <span style="color:#059669;font-weight:600;">Подключен</span>
        </div>
    </div>
    <div class="kpi-card">
        <div>
            <div class="kpi-label">Долговой портфель</div>
            <div class="kpi-val">{credit_val}</div>
            <div class="kpi-sub">{credit_sub}</div>
        </div>
        <div class="kpi-foot">
            <span>Процентный риск</span>
            <span style="color:#B91C1C;font-weight:600;">Высокий</span>
        </div>
    </div>
    <div class="kpi-radar">
        <div>
            <div style="font-size:11px;font-weight:700;color:#EF3124;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">
                Аналитическая сводка • {ROLES[current_role]}
            </div>
            <div style="font-size:14.5px;font-weight:600;color:#FFFFFF;line-height:1.35;">
                Ключевая ставка 14,0% и комплаенс расчетов в CNY затрагивают {current_company['supply_chain']['payers_cnt']} покупателей и импортные контракты компании.
            </div>
        </div>
        <div style="font-size:11.5px;color:#94A3B8;padding-top:8px;border-top:1px solid rgba(255,255,255,0.08);display:flex;justify-content:space-between;">
            <span>ОКВЭД {current_company['okved_code']}</span>
            <span>Доля рынка: {current_company['market_share']}</span>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# --- ПРОФИЛЬ И ГРАФ ЦЕПОЧКИ ПОСТАВОК ---
ctx_tab1, ctx_tab2 = st.tabs(["Контекст бизнеса", "Схема цепочки контрагентов"])
with ctx_tab1:
    st.markdown(
        f"""
        <div class="report-sheet" style="padding:16px 20px;">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
                <span style="font-size:13px;font-weight:700;color:#11141A;">Факторы чувствительности бизнеса: {current_company['name']}</span>
                <span style="font-size:12px;color:#64748B;">{current_company['group_id']} • {current_company['region']} • Штат: {current_company['workers_gradation']}</span>
            </div>
            <div>
                <span class="tag-accent">ОКВЭД {current_company['okved_code']}: {current_company['okved_name']}</span>
                <span class="tag-minimal">Выручка: {current_company['revenue_Text']}</span>
                <span class="tag-minimal">Рынок: {current_company['market_share']}</span>
                <span class="tag-minimal">Направления ВЭД: {current_company['fts_country']}</span>
                <span class="tag-minimal">Контрагенты: {current_company['supply_chain']['payers_cnt']} покупателей / {current_company['supply_chain']['beneficiaries_cnt']} поставщиков</span>
                <span class="tag-minimal">{current_company['supply_chain']['key_dependency']}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with ctx_tab2:
    st.markdown(
        f'<div class="report-sheet" style="padding:18px 22px;">'
        f'<div style="display:grid;grid-template-columns:1fr 64px 1fr 64px 1fr;align-items:center;">'
        f'<div style="display:flex;flex-direction:column;gap:8px;">'
        f'<div style="background:#EAECEF;border-left:3px solid #EF3124;border-radius:8px;padding:10px 14px;">'
        f'<div style="font-size:12px;font-weight:700;color:#11141A;">Покупатели строительного сектора</div>'
        f'<div style="font-size:11px;color:#B91C1C;">Риск роста отсрочки платежей при ставке 14%</div></div>'
        f'<div style="background:#EAECEF;border-left:3px solid #64748B;border-radius:8px;padding:10px 14px;">'
        f'<div style="font-size:12px;font-weight:700;color:#11141A;">Прочие заказчики ({current_company["supply_chain"]["payers_cnt"]} юрлиц)</div>'
        f'<div style="font-size:11px;color:#475569;">Плановый график поступлений выручки</div></div></div>'
        f'<svg viewBox="0 0 64 110" width="64" height="110"><path d="M 0 28 C 32 28, 32 55, 60 55" fill="none" stroke="#EF3124" stroke-width="1.8"/><path d="M 0 82 C 32 82, 32 55, 60 55" fill="none" stroke="#94A3B8" stroke-width="1.5"/></svg>'
        f'<div style="background:#16181F;color:#FFFFFF;border-radius:12px;padding:14px;text-align:center;">'
        f'<div style="font-size:13px;font-weight:700;">{current_company["name"]}</div>'
        f'<div style="font-size:11px;color:#94A3B8;margin-top:3px;">Выручка {current_company["revenue_Text"]}</div></div>'
        f'<svg viewBox="0 0 64 110" width="64" height="110"><path d="M 4 55 C 32 55, 32 28, 64 28" fill="none" stroke="#EF3124" stroke-width="1.8"/><path d="M 4 55 C 32 55, 32 82, 64 82" fill="none" stroke="#94A3B8" stroke-width="1.5"/></svg>'
        f'<div style="display:flex;flex-direction:column;gap:8px;">'
        f'<div style="background:#EAECEF;border-left:3px solid #EF3124;border-radius:8px;padding:10px 14px;">'
        f'<div style="font-size:12px;font-weight:700;color:#11141A;">Импортные поставщики ({current_company["fts_country"]})</div>'
        f'<div style="font-size:11px;color:#B91C1C;">Риск комплаенс-задержки расчетов в CNY</div></div>'
        f'<div style="background:#EAECEF;border-left:3px solid #64748B;border-radius:8px;padding:10px 14px;">'
        f'<div style="font-size:12px;font-weight:700;color:#11141A;">Внутренние подрядчики ({current_company["supply_chain"]["beneficiaries_cnt"]} юрлиц)</div>'
        f'<div style="font-size:11px;color:#475569;">Расчеты в рублях внутри РФ</div></div></div></div></div>',
        unsafe_allow_html=True,
    )


# --- РЕНДЕР СТРОГОГО АНАЛИТИЧЕСКОГО ЛИСТА (БЕЗ ИИ-ШАБЛОНОВ) ---
def render_insight_card(item: dict, idx: int):
    ins_id = item["insight_id"]
    b1 = item["block1_what_happened"]
    b2 = item["block2_why_important"]
    b3 = item["block3_consequences"]
    b4 = item["block4_alfa_vs_ai"]
    b5 = item["block5_actions_and_product"]
    b6 = item["block6_traceability"]
    prod = b5["bank_product"]

    facts_html = "".join([f"<li style='margin-bottom:4px;'>{f}</li>" for f in b1["facts"]])
    triggers_html = "".join([f'<span class="tag-minimal">{t}</span>' for t in b2["triggers"]])
    risks_li = "".join([f"<li style='margin-bottom:5px;'>{r}</li>" for r in b3["risks"]])
    opps_li = "".join([f"<li style='margin-bottom:5px;'>{o}</li>" for o in b3["opportunities"]])
    alfa_pos = b4["alfa_bank_position"]
    ai_pos = b4["ai_model_conclusion"]

    dot_color = "#EF3124" if item.get("is_critical") else "#64748B"

    # Единый строгий аналитический лист с тонкими разделителями 1px (как в Stripe / Bloomberg)
    st.markdown(
        f"""
        <div class="report-sheet">
            <div class="sheet-head">
                <div>
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                        <span style="display:inline-flex;align-items:center;gap:6px;font-size:11.5px;font-weight:700;color:{dot_color};text-transform:uppercase;letter-spacing:0.4px;">
                            <span style="width:7px;height:7px;border-radius:50%;background:{dot_color};display:inline-block;"></span>
                            {item['criticality']} • Релевантность {item['relevance_score']}%
                        </span>
                        <span style="font-size:12px;color:#64748B;">{item['category']} • {item['date']}</span>
                    </div>
                    <div style="font-size:18.5px;font-weight:700;color:#11141A;line-height:1.3;">
                        {item['title']}
                    </div>
                </div>
                <div style="text-align:right;flex-shrink:0;">
                    <div style="font-size:11px;color:#64748B;font-weight:600;">Оценка влияния</div>
                    <div style="font-size:14px;font-weight:700;color:#11141A;margin-top:2px;">{item.get('impact_metric', '')}</div>
                </div>
            </div>
            <div class="sheet-grid-2">
                <div class="sheet-cell">
                    <div class="cell-kicker">Событие и ключевые факты</div>
                    <p style="font-size:13.5px;line-height:1.5;color:#11141A;margin:0 0 8px 0;">{b1['summary']}</p>
                    <ul style="font-size:12.5px;line-height:1.45;padding-left:16px;margin:0 0 8px 0;color:#334155;">{facts_html}</ul>
                    <a href="{b1['source_url']}" target="_blank" style="font-size:12px;font-weight:600;color:#EF3124;text-decoration:none;">Источник: {b1['source_name']} ↗</a>
                </div>
                <div class="sheet-cell">
                    <div class="cell-kicker">Влияние на {current_company['name']}</div>
                    <p style="font-size:13.5px;line-height:1.5;color:#11141A;margin:0 0 12px 0;">{b2['explanation']}</p>
                    <div style="margin-top:8px;">{triggers_html}</div>
                </div>
            </div>
            <div class="sheet-grid-2">
                <div class="sheet-cell" style="border-left:3px solid #EF3124;">
                    <div class="cell-kicker" style="color:#B91C1C;">Факторы риска</div>
                    <ul style="font-size:13px;line-height:1.5;padding-left:16px;margin:0;color:#1E293B;">{risks_li}</ul>
                </div>
                <div class="sheet-cell" style="border-left:3px solid #059669;">
                    <div class="cell-kicker" style="color:#047857;">Финансовые возможности</div>
                    <ul style="font-size:13px;line-height:1.5;padding-left:16px;margin:0;color:#1E293B;">{opps_li}</ul>
                </div>
            </div>
            <div class="sheet-grid-2" style="border-bottom:none;background:#EDF0F6;">
                <div class="sheet-cell">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                        <span class="cell-kicker" style="color:#EF3124;margin:0;">Экспертная позиция Альфа-Банка</span>
                        <span style="font-size:11px;color:#64748B;">Аналитика ЦМИ</span>
                    </div>
                    <div style="font-size:12px;font-weight:600;color:#11141A;margin-bottom:6px;">{alfa_pos['report_title']}</div>
                    <div style="font-size:12.5px;color:#334155;line-height:1.45;border-left:2px solid #EF3124;padding-left:10px;">
                        {alfa_pos['quote']}
                    </div>
                </div>
                <div class="sheet-cell">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                        <span class="cell-kicker" style="color:#11141A;margin:0;">Расчетный прогноз для компании</span>
                        <span style="font-size:11px;color:#059669;font-weight:600;">{ai_pos['confidence']}</span>
                    </div>
                    <div style="font-size:12px;font-weight:600;color:#475569;margin-bottom:6px;">{ai_pos['model_name']}</div>
                    <div style="font-size:13px;color:#11141A;line-height:1.5;">
                        {ai_pos['conclusion']}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Нижняя панель инструментов карточки (Действия, Симулятор, Вопрос аналитику, Источники)
    t_act, t_sim, t_chat, t_trace = st.tabs([
        f"Рекомендации ({ROLES[current_role]}) и продукт банка",
        "Калькулятор эффекта (P&L)",
        "Вопрос аналитику",
        "Источники и трассировка",
    ])

    with t_act:
        ac1, ac2 = st.columns([1.3, 1.0])
        with ac1:
            for step_i, step_text in enumerate(b5["checklist"]):
                st.checkbox(step_text, value=(step_i == 0), key=f"chk_{ins_id}_{current_role}_{step_i}")
        with ac2:
            st.markdown(
                f"""
                <div style="background:#16181F;color:#FFFFFF;border-radius:12px;padding:14px 18px;margin-bottom:8px;">
                    <div style="font-size:11px;color:#94A3B8;font-weight:600;">Рекомендуемый инструмент Альфа-Бизнеса</div>
                    <div style="font-size:14.5px;font-weight:700;color:#FFFFFF;margin:3px 0;">{prod['title']}</div>
                    <div style="font-size:12px;color:#CBD5E1;line-height:1.4;">{prod['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(prod["cta"], key=f"cta_{ins_id}_{idx}", type="primary", use_container_width=True):
                st.success(f"Заявка по инструменту «{prod['title']}» передана вашему персональному менеджеру в Альфа-Бизнесе.")

    with t_sim:
        sc1, sc2, sc3 = st.columns([1.1, 1.1, 1.4])
        with sc1:
            hedge_share = st.slider("Доля хеджирования портфеля (%)", 0, 100, 60, 10, key=f"sh_{ins_id}_{idx}")
        with sc2:
            stress_level = st.slider("Горизонт расчета (мес.)", 3, 12, 6, 3, key=f"sm_{ins_id}_{idx}")
        base_loss = 7.2 * stress_level
        saved_amount = round(base_loss * (hedge_share / 100.0) * 0.82, 1)
        net_exposure = round(base_loss - saved_amount, 1)
        with sc3:
            st.markdown(
                f"""
                <div class="report-sheet" style="padding:12px 16px;margin:0;">
                    <div style="display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:4px;">
                        <span>Потенциальный риск без хеджирования:</span><b style="color:#B91C1C;">-{base_loss:.1f} млн ₽</b>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:4px;">
                        <span>Экономия при подключении инструмента:</span><b style="color:#059669;">+{saved_amount:.1f} млн ₽</b>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:12.5px;border-top:1px solid #DEE3EC;padding-top:4px;">
                        <span>Остаточная нагрузка на EBITDA:</span><b>-{net_exposure:.1f} млн ₽</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with t_chat:
        pc1, pc2, pc3 = st.columns(3)
        preset_q = None
        with pc1:
            if st.button("Влияние на долговую нагрузку", key=f"p1_{ins_id}_{idx}", use_container_width=True):
                preset_q = "Рассчитай влияние на нашу долговую нагрузку"
        with pc2:
            if st.button("Риски по цепочке контрагентов", key=f"p2_{ins_id}_{idx}", use_container_width=True):
                preset_q = "Как это отразится на наших поставщиках и покупателях?"
        with pc3:
            if st.button("Базовые отчеты ЦМИ Банка", key=f"p3_{ins_id}_{idx}", use_container_width=True):
                preset_q = "Какие макро-отчеты Альфа-Банка подтверждают этот вывод?"

        qc1, qc2 = st.columns([3.6, 1.0])
        with qc1:
            custom_q = st.text_input("Вопрос по событию", placeholder="Введите уточняющий вопрос...", key=f"iq_{ins_id}_{idx}", label_visibility="collapsed")
        with qc2:
            send_clicked = st.button("Отправить", key=f"sq_{ins_id}_{idx}", type="primary", use_container_width=True)

        final_q = preset_q or (custom_q if send_clicked and custom_q.strip() else None)
        if final_q:
            res = api_post_chat(current_company["company_id"], current_role, ins_id, final_q)
            st.session_state.chat_history[ins_id] = {"q": final_q, "a": res.get("answer", "")}

        if ins_id in st.session_state.chat_history:
            st.markdown(st.session_state.chat_history[ins_id]["a"])

    with t_trace:
        tc1, tc2 = st.columns([1.3, 1.0])
        with tc1:
            for step_obj in b6["agent_steps"]:
                st.markdown(f"- **{step_obj['stage']}:** {step_obj['detail']}")
        with tc2:
            for feat in b6["csv_features_used"]:
                st.code(feat, language="text")

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)


if nav_mode == "Аналитическая лента":
    feed_items = st.session_state.custom_insights + api_get_feed(
        current_company["company_id"], current_role
    )
    if filter_crit:
        feed_items = [x for x in feed_items if x.get("is_critical")]

    for idx, insight in enumerate(feed_items):
        render_insight_card(insight, idx)

elif nav_mode == "Разбор внешнего материала":
    with st.form("live_news_form"):
        new_title = st.text_input(
            "Заголовок материала",
            value="Минпромторг и ФТС обсуждают изменение пошлин и субсидирования логистики для промышленного экспорта с 4 квартала 2026 года",
        )
        new_text = st.text_area(
            "Текст новости или документа",
            height=110,
            value=(
                "Правительство рассматривает пакет мер по перенастройке транспортных субсидий и таможенных пошлин "
                "для крупных промышленных и аграрных экспортеров, работающих на восточном и южном направлениях."
            ),
        )
        new_url = st.text_input("Источник", value="https://www.rbc.ru/economics/")
        submitted = st.form_submit_button("Выполнить анализ влияния на компанию", type="primary")

    if submitted:
        live_card = analyze_custom_news_Realtime(
            current_company["company_id"], current_role, new_title, new_text, new_url
        )
        st.session_state.custom_insights = [live_card]

    if st.session_state.custom_insights:
        render_insight_card(st.session_state.custom_insights[0], 999)

elif nav_mode == "Метрики и безопасность":
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Точность отбора (Precision@3)", "92.4%")
    m2.metric("Верификация фактов", "98.7%")
    m3.metric("Конверсия в продукты", "18.5%")
    m4.metric("Среднее время отклика", "1.3 сек")
