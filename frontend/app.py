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
    page_title="Альфа-Бизнес | Альфа-Инсайт",
    page_icon="alfa-bank.svg" if Path("alfa-bank.svg").exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BASE_DIR = Path(__file__).parent


def load_svg_base64(filename: str) -> str:
    svg_path = BASE_DIR / filename
    if svg_path.exists():
        data = svg_path.read_bytes()
        return f"data:image/svg+xml;base64,{base64.b64encode(data).decode('utf-8')}"
    return ""


ALFA_LOGO_B64 = load_svg_base64("alfa-bank.svg")
ALFA_BIZ_LOGO_B64 = load_svg_base64("alfa-bank-business.svg")

SVG = {
    "bell": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
    "bolt": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "building": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#EF3124" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M8 10h.01"/><path d="M16 10h.01"/><path d="M8 14h.01"/><path d="M16 14h.01"/></svg>',
    "user": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#1D1D1F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "layers": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#EF3124" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
    "doc": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#1D1D1F" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
    "target": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#EF3124" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "risk": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "trend_up": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "shield": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "cpu": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>',
    "check": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "link": '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#EF3124" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>',
    "dot_green": '<svg width="8" height="8" viewBox="0 0 8 8"><circle cx="4" cy="4" r="4" fill="#10B981"/></svg>',
    "dot_red": '<svg width="8" height="8" viewBox="0 0 8 8"><circle cx="4" cy="4" r="4" fill="#EF3124"/></svg>',
}

if "selected_company_id" not in st.session_state:
    st.session_state.selected_company_id = COMPANIES[0]["company_id"]
if "selected_role" not in st.session_state:
    st.session_state.selected_role = "CFO"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "custom_insights" not in st.session_state:
    st.session_state.custom_insights = []
if "feedback_Given" not in st.session_state:
    st.session_state.feedback_Given = {}


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
    header[data-testid="stHeader"] {
        background: transparent;
        height: 0px;
    }
    .stDeployButton, div[data-testid="stToolbar"] {
        display: none;
    }

    html, body, .stApp, [class*="css"], div, p, span, h1, h2, h3, h4, label, button, input, textarea, li, blockquote {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "SF Pro", "Helvetica Neue", sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        font-feature-settings: "kern" 1, "liga" 1, "calt" 1;
    }

    html, body, .stApp {
        background-color: #F5F5F7;
        color: #1D1D1F;
    }

    code, pre {
        font-family: "SF Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 4rem;
        max-width: 1360px;
    }

    label, .stSelectbox label, .stCheckbox label, .stTextInput label, .stTextArea label {
        color: #1D1D1F;
    }
    div[data-testid="stWidgetLabel"] p {
        color: #1D1D1F;
        font-weight: 600;
        font-size: 13px;
        letter-spacing: -0.1px;
    }

    div[data-baseweb="select"] > div {
        background-color: #FFFFFF;
        color: #1D1D1F;
        border: 1px solid #D2D2D7;
        border-radius: 12px;
        min-height: 44px;
        font-weight: 600;
        font-size: 14px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
        transition: all 0.15s ease;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #86868B;
    }
    div[data-baseweb="select"] span {
        color: #1D1D1F;
    }

    input, textarea {
        background-color: #FFFFFF;
        color: #1D1D1F;
    }

    section[data-testid="stSidebar"] {
        background-color: #141416;
        border-right: 1px solid #27272A;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] p {
        color: #F4F4F5;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #232326;
        border-color: #3F3F46;
        color: #FFFFFF;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #FFFFFF;
    }

    .alfa-nav-header {
        background: #141416;
        color: #FFFFFF;
        padding: 18px 26px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .alfa-nav-left {
        display: flex;
        align-items: center;
        gap: 16px;
        min-width: 0;
    }
    .alfa-nav-title {
        font-size: 19px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.3px;
        margin: 0 0 3px 0;
    }
    .alfa-nav-sub {
        font-size: 13px;
        color: #A1A1AA;
        margin: 0;
        font-weight: 400;
    }
    .alfa-alert-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        white-space: nowrap;
        background: #EF3124;
        border: 1px solid rgba(255, 255, 255, 0.22);
        color: #FFFFFF;
        padding: 8px 16px;
        border-radius: 999px;
        font-size: 12.5px;
        font-weight: 700;
        flex-shrink: 0;
        box-shadow: 0 4px 14px rgba(239, 49, 36, 0.4);
    }
    .alfa-alert-pill span, .alfa-alert-pill svg {
        color: #FFFFFF;
        stroke: #FFFFFF;
    }

    .bento-card {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 18px 20px;
        border: 1px solid rgba(0, 0, 0, 0.06);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        overflow: hidden;
    }
    .bento-label {
        font-size: 11.5px;
        color: #6E6E73;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .bento-value {
        font-size: 19px;
        font-weight: 800;
        color: #1D1D1F;
        letter-spacing: -0.5px;
        margin: 6px 0 4px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .bento-sub {
        font-size: 12px;
        color: #48484A;
        font-weight: 500;
        margin-bottom: 6px;
    }
    .bento-meta {
        font-size: 12px;
        color: #6E6E73;
        display: flex;
        align-items: center;
        gap: 6px;
        font-weight: 500;
    }

    .insight-hero-widget {
        background: linear-gradient(135deg, #18181B 0%, #271717 60%, #991B1B 100%);
        color: #FFFFFF;
        border-radius: 18px;
        padding: 20px 24px;
        box-shadow: 0 12px 28px rgba(239, 49, 36, 0.15);
        border: 1px solid rgba(239, 49, 36, 0.35);
        height: 100%;
    }
    .hero-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #EF3124;
        color: #FFFFFF;
        font-size: 11px;
        font-weight: 700;
        padding: 5px 12px;
        border-radius: 999px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .hero-tag span, .hero-tag svg {
        color: #FFFFFF;
        stroke: #FFFFFF;
    }
    .hero-title {
        font-size: 17px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.2px;
        margin-bottom: 6px;
    }
    .hero-desc {
        font-size: 13px;
        color: #E4E4E7;
        line-height: 1.45;
    }

    .profile-bento {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 18px 22px;
        margin-top: 16px;
        margin-bottom: 24px;
        border: 1px solid rgba(0, 0, 0, 0.06);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
    }
    .profile-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 12px;
    }
    .profile-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        font-weight: 700;
        color: #1D1D1F;
    }
    .chip-red {
        display: inline-flex;
        align-items: center;
        background-color: #FFF1F0;
        color: #D9261A;
        border: 1px solid #FFCCC7;
        padding: 5px 11px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .chip-neutral {
        display: inline-flex;
        align-items: center;
        background-color: #F5F5F7;
        color: #1D1D1F;
        border: 1px solid #E5E5EA;
        padding: 5px 11px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    .insight-header-box {
        background: #FFFFFF;
        padding: 24px 26px 18px 26px;
        border-radius: 20px;
        border: 1px solid rgba(0, 0, 0, 0.07);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
        margin-bottom: 12px;
    }
    .badge-CRITICAL {
        background-color: #EF3124;
        color: #FFFFFF;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 11px;
        letter-spacing: 0.3px;
    }
    .badge-HIGH {
        background-color: #F97316;
        color: #FFFFFF;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 11px;
    }
    .badge-MEDIUM {
        background-color: #2563EB;
        color: #FFFFFF;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 11px;
    }

    .block-card {
        background: #FFFFFF;
        border: 1px solid rgba(0, 0, 0, 0.07);
        border-radius: 16px;
        padding: 18px 20px;
        height: 100%;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    }
    .block-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #6E6E73;
        margin-bottom: 10px;
    }

    .risk-panel {
        background: #FFFBFB;
        border: 1px solid #FECACA;
        border-left: 4px solid #EF3124;
        border-radius: 16px;
        padding: 18px 20px;
        height: 100%;
    }
    .opp-panel {
        background: #F9FEFB;
        border: 1px solid #A7F3D0;
        border-left: 4px solid #10B981;
        border-radius: 16px;
        padding: 18px 20px;
        height: 100%;
    }

    .alfa-pos-panel {
        background: #FFFFFF;
        border: 1.5px solid #EF3124;
        border-radius: 16px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 4px 14px rgba(239, 49, 36, 0.06);
    }
    .ai-pos-panel {
        background: #FFFFFF;
        border: 1.5px solid #1D1D1F;
        border-radius: 16px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
    }

    .product-cta-card {
        background: #141416;
        color: #FFFFFF;
        border-radius: 16px;
        padding: 18px 22px;
        border-left: 4px solid #EF3124;
        margin-bottom: 10px;
    }

    div.stButton > button[kind="primary"] {
        background-color: #EF3124;
        color: #FFFFFF;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        font-size: 13.5px;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 12px rgba(239, 49, 36, 0.22);
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #D9261A;
        color: #FFFFFF;
    }
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF;
        color: #1D1D1F;
        border: 1px solid #D2D2D7;
        border-radius: 10px;
        font-weight: 500;
        font-size: 13px;
    }

    div[data-testid="stExpander"] {
        background: #FFFFFF;
        border: 1px solid rgba(0, 0, 0, 0.07);
        border-radius: 14px;
        margin-top: 8px;
    }
    div[data-testid="stExpander"] summary p {
        color: #1D1D1F;
        font-weight: 600;
        font-size: 13.5px;
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
            f'<div style="display:flex;align-items:center;gap:12px;padding:6px 0 16px 0;border-bottom:1px solid #27272A;margin-bottom:16px;">'
            f'<div style="width:42px;height:42px;border-radius:12px;overflow:hidden;flex-shrink:0;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,0.25);"><img src="{ALFA_BIZ_LOGO_B64}" style="width:100%;height:100%;object-fit:cover;display:block;"/></div>'
            f'<div><div style="font-weight:700;font-size:16px;color:#FFFFFF;letter-spacing:-0.2px;">Альфа-Бизнес</div>'
            f'<div style="font-size:12px;color:#A1A1AA;">Корпоративный портал</div></div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="font-size:11px;font-weight:700;color:#71717A;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;">Разделы сервиса</div>', unsafe_allow_html=True)
    nav_mode = st.radio(
        "Навигация",
        options=[
            "Главный экран • Альфа-Инсайт",
            "Анализ внешнего события",
            "Мониторинг и безопасность",
        ],
        label_visibility="collapsed",
    )

    st.markdown('<div style="height:16px;border-bottom:1px solid #27272A;margin-bottom:16px;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:11px;font-weight:700;color:#71717A;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;">Профиль пользователя</div>', unsafe_allow_html=True)

    selected_comp_id = st.selectbox(
        "Компания",
        options=list(company_map.keys()),
        format_func=lambda cid: f"{company_map[cid]['name']} ({company_map[cid]['revenue_Text']})",
        index=list(company_map.keys()).index(st.session_state.selected_company_id),
    )
    st.session_state.selected_company_id = selected_comp_id

    selected_role_key = st.selectbox(
        "Должность (Роль ЛПР)",
        options=list(ROLES.keys()),
        format_func=lambda r: ROLES[r],
        index=list(ROLES.keys()).index(st.session_state.selected_role),
    )
    st.session_state.selected_role = selected_role_key

    current_company = company_map[selected_comp_id]

# --- ВЕРХНИЙ ХЕДЕР АЛЬФА-БИЗНЕС ---
logo_html = (
    f'<div style="width:44px;height:44px;border-radius:12px;overflow:hidden;flex-shrink:0;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(239,49,36,0.35);"><img src="{ALFA_LOGO_B64}" style="width:100%;height:100%;object-fit:cover;display:block;"/></div>'
    if ALFA_LOGO_B64
    else '<div style="width:44px;height:44px;border-radius:12px;background:#EF3124;color:#FFF;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:20px;">A</div>'
)

st.markdown(
    f"""
<div class="alfa-nav-header">
    <div class="alfa-nav-left">
        {logo_html}
        <div>
            <div class="alfa-nav-title">Альфа-Бизнес • Корпоративная аналитика</div>
            <div class="alfa-nav-sub">{current_company['name']} • Выручка: {current_company['revenue_Text']} • {ROLES[selected_role_key]}</div>
        </div>
    </div>
    <div class="alfa-alert-pill">
        {SVG['bell']}
        <span>2 критичных инсайта</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# --- ПАНЕЛЬ БЫСТРОГО ПЕРЕКЛЮЧЕНИЯ КОНТЕКСТА ---
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2.3, 2.3, 1.2])
with ctrl_col1:
    st.markdown(f'<div style="display:flex;align-items:center;gap:6px;font-size:12.5px;font-weight:600;color:#1D1D1F;margin-bottom:4px;">{SVG["building"]} <span>Юридическое лицо / Холдинг</span></div>', unsafe_allow_html=True)
    top_comp = st.selectbox(
        "Юридическое лицо",
        options=list(company_map.keys()),
        format_func=lambda cid: f"{company_map[cid]['name']} — {company_map[cid]['okved_name'][:42]}",
        index=list(company_map.keys()).index(st.session_state.selected_company_id),
        key="top_comp_select",
        label_visibility="collapsed",
    )
    if top_comp != st.session_state.selected_company_id:
        st.session_state.selected_company_id = top_comp
        st.rerun()

with ctrl_col2:
    st.markdown(f'<div style="display:flex;align-items:center;gap:6px;font-size:12.5px;font-weight:600;color:#1D1D1F;margin-bottom:4px;">{SVG["user"]} <span>Роль руководителя (ЛПР)</span></div>', unsafe_allow_html=True)
    top_role = st.selectbox(
        "Роль ЛПР",
        options=list(ROLES.keys()),
        format_func=lambda r: ROLES[r],
        index=list(ROLES.keys()).index(st.session_state.selected_role),
        key="top_role_select",
        label_visibility="collapsed",
    )
    if top_role != st.session_state.selected_role:
        st.session_state.selected_role = top_role
        st.rerun()

with ctrl_col3:
    st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
    filter_crit = st.checkbox("Только критичные", value=False)

current_company = company_map[st.session_state.selected_company_id]
current_role = st.session_state.selected_role

st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

# --- BENTO-СЕТКА СЧЕТОВ И ВИДЖЕТА АЛЬФА-ИНСАЙТ ---
credit_val = current_company["accounts_summary"].get("active_credit_line", "")
credit_sub = current_company["accounts_summary"].get("credit_sub", "Плавающая ставка ЦБ")

acc_col1, acc_col2, acc_col3, widget_col = st.columns([1.05, 1.05, 1.15, 2.15])
with acc_col1:
    st.markdown(
        f"""
    <div class="bento-card">
        <div>
            <div class="bento-label">Расчетный счет RUB</div>
            <div class="bento-value">{current_company['accounts_summary']['ruble_balance']}</div>
            <div class="bento-sub">РКО и ликвидность</div>
        </div>
        <div class="bento-meta">{SVG['dot_green']} <span>Доступно к платежам</span></div>
    </div>
    """,
        unsafe_allow_html=True,
    )
with acc_col2:
    st.markdown(
        f"""
    <div class="bento-card">
        <div>
            <div class="bento-label">Валютный счет CNY</div>
            <div class="bento-value">{current_company['accounts_summary']['cny_balance']}</div>
            <div class="bento-sub">Контракты ВЭД</div>
        </div>
        <div class="bento-meta"><span>Направления: {current_company['fts_country']}</span></div>
    </div>
    """,
        unsafe_allow_html=True,
    )
with acc_col3:
    st.markdown(
        f"""
    <div class="bento-card">
        <div>
            <div class="bento-label">Долговой портфель</div>
            <div class="bento-value">{credit_val}</div>
            <div class="bento-sub">{credit_sub}</div>
        </div>
        <div class="bento-meta" style="color:#D9261A;">{SVG['dot_red']} <span>Чувствительность к ставке ЦБ</span></div>
    </div>
    """,
        unsafe_allow_html=True,
    )
with widget_col:
    st.markdown(
        f"""
    <div class="insight-hero-widget">
        <div class="hero-tag">{SVG['bolt']} <span>Альфа-Инсайт • Умная аналитика</span></div>
        <div class="hero-title">Персональная сводка: {ROLES[current_role]}</div>
        <div class="hero-desc">
            Выявлено <b>2 критичных события</b> (Ключевая ставка ЦБ РФ 14% и комплаенс расчетов в CNY), напрямую влияющих на отрасль ОКВЭД <b>{current_company['okved_code']}</b> и цепочку из <b>{current_company['supply_chain']['payers_cnt']} контрагентов</b>.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# --- ПАСПОРТ ЦИФРОВОГО ПРОФИЛЯ КОМПАНИИ ---
st.markdown(
    f"""
<div class="profile-bento">
    <div class="profile-header">
        <div class="profile-title">
            {SVG['layers']}
            <span>Бизнес-профиль компании и активные факторы чувствительности</span>
        </div>
        <div style="font-size:12px;color:#6E6E73;font-weight:500;">
            Холдинг: <b style="color:#1D1D1F;">{current_company['group_id']}</b> • Регион: <b style="color:#1D1D1F;">{current_company['region']}</b>
        </div>
    </div>
    <div>
        <span class="chip-red">ОКВЭД {current_company['okved_code']}: {current_company['okved_name']}</span>
        <span class="chip-neutral">Выручка: {current_company['revenue_Text']}</span>
        <span class="chip-neutral">Доля рынка: {current_company['market_share']}</span>
        <span class="chip-neutral">ВЭД: {current_company['fts_country']}</span>
        <span class="chip-neutral">Цепочка расчетов: {current_company['supply_chain']['payers_cnt']} покупателей / {current_company['supply_chain']['beneficiaries_cnt']} поставщиков</span>
        <span class="chip-neutral">Ключевой фактор: {current_company['supply_chain']['key_dependency']}</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


def render_insight_card(item: dict, idx: int):
    ins_id = item["insight_id"]
    crit = item.get("criticality", "HIGH")

    with st.container():
        st.markdown(
            f"""
        <div class="insight-header-box">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span class="badge-{crit}">{crit} • ИНДЕКС ЗНАЧИМОСТИ {item['relevance_score']}%</span>
                    <span style="font-size:12.5px;color:#6E6E73;font-weight:500;">{item['category']} • {item['date']}</span>
                </div>
                <span class="chip-red" style="margin:0;">{item.get('role_focus_badge', '')}</span>
            </div>
            <div style="font-size:20px;font-weight:700;color:#1D1D1F;letter-spacing:-0.3px;line-height:1.3;">
                {item['title']}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        b1_col, b2_col = st.columns([1.15, 1.0])
        b1 = item["block1_what_happened"]
        b2 = item["block2_why_important"]

        with b1_col:
            facts_html = "".join([f"<li style='margin-bottom:5px;color:#1D1D1F;'>{f}</li>" for f in b1["facts"]])
            st.markdown(
                f"""
            <div class="block-card">
                <div class="block-title">{SVG['doc']} <span>Что произошло (Факты и первоисточник)</span></div>
                <p style="font-size:14px;line-height:1.55;color:#1D1D1F;margin-bottom:10px;">{b1['summary']}</p>
                <ul style="font-size:13px;line-height:1.5;padding-left:18px;margin-bottom:12px;">
                    {facts_html}
                </ul>
                <div style="font-size:12.5px;font-weight:600;display:flex;align-items:center;gap:6px;">
                    {SVG['link']}
                    <a href="{b1['source_url']}" target="_blank" style="color:#EF3124;text-decoration:none;">Первоисточник: {b1['source_name']}</a>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with b2_col:
            triggers_html = "".join([f'<span class="chip-red">{t}</span>' for t in b2["triggers"]])
            st.markdown(
                f"""
            <div class="block-card">
                <div class="block-title">{SVG['target']} <span>Почему это важно для {current_company['name']}</span></div>
                <p style="font-size:14px;line-height:1.55;color:#1D1D1F;margin-bottom:14px;">{b2['explanation']}</p>
                <div style="font-size:11.5px;color:#6E6E73;margin-bottom:8px;font-weight:600;text-transform:uppercase;letter-spacing:0.4px;">Сработавшие триггеры профиля:</div>
                <div>{triggers_html}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        b3 = item["block3_consequences"]
        r_col, o_col = st.columns(2)
        with r_col:
            risks_li = "".join([f"<li style='margin-bottom:6px;color:#7F1D1D;'>{r}</li>" for r in b3["risks"]])
            st.markdown(
                f"""
            <div class="risk-panel">
                <div style="display:flex;align-items:center;gap:8px;font-weight:700;color:#DC2626;font-size:13px;text-transform:uppercase;letter-spacing:0.4px;margin-bottom:10px;">
                    {SVG['risk']} <span>Ключевые риски для бизнеса</span>
                </div>
                <ul style="font-size:13.5px;line-height:1.5;padding-left:18px;margin:0;">
                    {risks_li}
                </ul>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with o_col:
            opps_li = "".join([f"<li style='margin-bottom:6px;color:#064E3B;'>{o}</li>" for o in b3["opportunities"]])
            st.markdown(
                f"""
            <div class="opp-panel">
                <div style="display:flex;align-items:center;gap:8px;font-weight:700;color:#059669;font-size:13px;text-transform:uppercase;letter-spacing:0.4px;margin-bottom:10px;">
                    {SVG['trend_up']} <span>Окна возможностей</span>
                </div>
                <ul style="font-size:13.5px;line-height:1.5;padding-left:18px;margin:0;">
                    {opps_li}
                </ul>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        b4 = item["block4_alfa_vs_ai"]
        alfa_pos = b4["alfa_bank_position"]
        ai_pos = b4["ai_model_conclusion"]

        alfa_col, ai_col = st.columns(2)
        with alfa_col:
            st.markdown(
                f"""
            <div class="alfa-pos-panel">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                    <span style="display:inline-flex;align-items:center;gap:6px;background:#EF3124;color:#FFFFFF;padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700;">
                        {SVG['shield']} <span style="color:#FFFFFF;">ЭКСПЕРТНАЯ ПОЗИЦИЯ АЛЬФА-БАНКА</span>
                    </span>
                    <span style="font-size:11px;color:#6E6E73;font-weight:600;">Аналитика ЦМИ</span>
                </div>
                <div style="font-size:12.5px;font-weight:700;color:#1D1D1F;margin-bottom:8px;">
                    Материал: {alfa_pos['report_title']}
                </div>
                <blockquote style="font-size:13.5px;font-style:italic;color:#3A3A3C;border-left:3px solid #EF3124;padding-left:12px;margin:0 0 10px 0;line-height:1.5;">
                    {alfa_pos['quote']}
                </blockquote>
                <div style="font-size:11.5px;color:#6E6E73;font-weight:600;">
                    {alfa_pos['analyst_team']}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with ai_col:
            st.markdown(
                f"""
            <div class="ai-pos-panel">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                    <span style="display:inline-flex;align-items:center;gap:6px;background:#1D1D1F;color:#FFFFFF;padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700;">
                        {SVG['cpu']} <span style="color:#FFFFFF;">ПЕРСОНАЛЬНЫЙ ВЫВОД AI-МОДЕЛИ</span>
                    </span>
                    <span style="font-size:11px;color:#059669;font-weight:700;">Точность: {ai_pos['confidence']}</span>
                </div>
                <div style="font-size:12.5px;font-weight:700;color:#1D1D1F;margin-bottom:8px;">
                    Аналитический контур: {ai_pos['model_name']}
                </div>
                <p style="font-size:13.5px;color:#1D1D1F;line-height:1.55;margin:0;">
                    {ai_pos['conclusion']}
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        b5 = item["block5_actions_and_product"]
        prod = b5["bank_product"]
        act_col, prod_col = st.columns([1.2, 1.0])

        with act_col:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;font-size:13.5px;font-weight:700;color:#1D1D1F;margin-bottom:8px;">{SVG["check"]} <span>Рекомендуемые действия ({ROLES[current_role]})</span></div>',
                unsafe_allow_html=True,
            )
            for step_i, step_text in enumerate(b5["checklist"]):
                st.checkbox(
                    step_text,
                    value=(step_i == 0),
                    key=f"chk_{ins_id}_{current_role}_{step_i}",
                )

        with prod_col:
            st.markdown(
                f"""
            <div class="product-cta-card">
                <div style="font-size:11px;color:#FF6B60;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">
                    Решение Альфа-Бизнеса
                </div>
                <div style="font-size:16px;font-weight:700;color:#FFFFFF;margin:4px 0 6px 0;">
                    {prod['title']}
                </div>
                <div style="font-size:12.5px;color:#D4D4D8;line-height:1.45;">
                    {prod['desc']}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            if st.button(f"{prod['cta']}", key=f"cta_{ins_id}_{idx}", type="primary", use_container_width=True):
                st.toast(f"Заявка «{prod['title']}» для {current_company['name']} передана персональному менеджеру.")

        b6 = item["block6_traceability"]
        with st.expander("Цепочка рассуждений AI-модели и источники данных (Traceability)"):
            t_col1, t_col2 = st.columns([1.3, 1.0])
            with t_col1:
                st.markdown("**Этапы формирования вывода:**")
                for step_obj in b6["agent_steps"]:
                    st.markdown(f"- **{step_obj['stage']}:** {step_obj['detail']}")
            with t_col2:
                st.markdown("**Задействованные параметры компании:**")
                for feat in b6["csv_features_used"]:
                    st.code(feat, language="text")
                st.markdown("**Проверенные источники:**")
                for src in b6["sources_verified"]:
                    st.markdown(f"- {src}")

        with st.expander("Задать уточняющий вопрос AI-аналитику"):
            p_col1, p_col2, p_col3 = st.columns(3)
            preset_q = None
            with p_col1:
                if st.button("Рассчитать влияние на долг", key=f"p1_{ins_id}_{idx}", use_container_width=True):
                    preset_q = "Рассчитай влияние на нашу долговую нагрузку"
            with p_col2:
                if st.button("Влияние на цепочку контрагентов", key=f"p2_{ins_id}_{idx}", use_container_width=True):
                    preset_q = "Как это отразится на наших поставщиках и покупателях?"
            with p_col3:
                if st.button("Сверка с прогнозом ЦМИ Альфа-Банка", key=f"p3_{ins_id}_{idx}", use_container_width=True):
                    preset_q = "Какие макро-отчеты Альфа-Банка подтверждают этот вывод?"

            custom_q = st.text_input(
                "Ваш вопрос:",
                placeholder="Например: Какой объем ликвидности в CNY оптимально захеджировать до конца квартала?",
                key=f"input_q_{ins_id}_{idx}",
            )
            send_clicked = st.button("Отправить запрос", key=f"send_q_{ins_id}_{idx}", type="primary")

            final_q = preset_q or (custom_q if send_clicked and custom_q.strip() else None)
            if final_q:
                with st.spinner("Анализ профиля компании и аналитических материалов Альфа-Банка..."):
                    res = api_post_chat(
                        current_company["company_id"],
                        current_role,
                        ins_id,
                        final_q,
                    )
                    st.session_state.chat_history[ins_id] = {
                        "q": final_q,
                        "a": res.get("answer", ""),
                        "models": res.get("used_models", []),
                        "trace_id": res.get("trace_id", ""),
                    }

            if ins_id in st.session_state.chat_history:
                chat_item = st.session_state.chat_history[ins_id]
                st.markdown(f"**Вопрос:** {chat_item['q']}")
                st.markdown(chat_item["a"])
                st.caption(f"Trace ID: {chat_item['trace_id']}")

        fb_col1, fb_col2, fb_col3 = st.columns([3.2, 1.0, 1.0])
        with fb_col1:
            st.caption("Оцените релевантность инсайта для настройки персональной ленты:")
        with fb_col2:
            if st.button("Полезно", key=f"like_{ins_id}_{idx}", use_container_width=True):
                st.session_state.feedback_Given[ins_id] = "LIKE"
                st.toast("Оценка сохранена.")
        with fb_col3:
            if st.button("Скрыть похожие", key=f"dislike_{ins_id}_{idx}", use_container_width=True):
                st.session_state.feedback_Given[ins_id] = "DISLIKE"
                st.toast("Предпочтения обновлены.")

        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)


if nav_mode == "Главный экран • Альфа-Инсайт":
    feed_items = st.session_state.custom_insights + api_get_feed(
        current_company["company_id"], current_role
    )
    if filter_crit:
        feed_items = [x for x in feed_items if x.get("criticality") == "CRITICAL"]

    st.markdown(
        f'<div style="font-size:18px;font-weight:700;color:#1D1D1F;letter-spacing:-0.3px;margin-bottom:14px;">Персональная лента бизнес-инсайтов ({len(feed_items)})</div>',
        unsafe_allow_html=True,
    )
    for idx, insight in enumerate(feed_items):
        render_insight_card(insight, idx)

elif nav_mode == "Анализ внешнего события":
    st.markdown(
        '<div style="font-size:18px;font-weight:700;color:#1D1D1F;margin-bottom:8px;">Анализ произвольной новости или документа</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "Добавьте текст любой рыночной новости или регуляторного релиза. Система автоматически сопоставит событие с финансовым профилем компании, графом контрагентов и аналитикой Альфа-Банка."
    )
    with st.form("live_news_form"):
        new_title = st.text_input(
            "Заголовок события",
            value="Минпромторг и ФТС обсуждают изменение пошлин и субсидирования логистики для промышленного экспорта с 4 квартала 2026 года",
        )
        new_text = st.text_area(
            "Текст материала",
            height=120,
            value=(
                "Правительство рассматривает пакет мер по перенастройке транспортных субсидий и таможенных пошлин "
                "для крупных промышленных и аграрных экспортеров, работающих на восточном и южном направлениях. "
                "Приоритет в субсидировании процентных ставок и логистики получат компании с локализацией поставок "
                "и прозрачным контуром расчетов."
            ),
        )
        new_url = st.text_input("Ссылка на источник", value="https://www.rbc.ru/economics/")
        submitted = st.form_submit_button("Сформировать персональный инсайт", type="primary")

    if submitted:
        with st.spinner("Сопоставление с профилем компании и аналитикой Альфа-Банка..."):
            live_card = analyze_custom_news_Realtime(
                current_company["company_id"],
                current_role,
                new_title,
                new_text,
                new_url,
            )
            st.session_state.custom_insights = [live_card]
        st.success("Аналитический разбор сформирован и добавлен в ленту.")

    if st.session_state.custom_insights:
        render_insight_card(st.session_state.custom_insights[0], 999)

elif nav_mode == "Мониторинг и безопасность":
    st.markdown(
        '<div style="font-size:18px;font-weight:700;color:#1D1D1F;margin-bottom:14px;">Мониторинг качества аналитики и защита данных</div>',
        unsafe_allow_html=True,
    )
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Точность персонализации", "92.4%", "+3.1% за неделю")
    m2.metric("Верификация фактов", "98.7%", "Self-Check активен")
    m3.metric("Конверсия в решения банка", "18.5%", "+4.2%")
    m4.metric("Среднее время анализа", "1.8 сек", "-0.4 сек")

    sec_col1, sec_col2 = st.columns(2)
    with sec_col1:
        st.markdown(
            """
        <div class="block-card">
            <div class="block-title">Контур информационной безопасности</div>
            <ul style="font-size:13.5px;line-height:1.65;color:#1D1D1F;padding-left:18px;">
                <li><b>Ролевой доступ (RBAC):</b> разграничение аналитических срезов и финансовых показателей между ролями CEO, CFO, Казначейства и Главного бухгалтера.</li>
                <li><b>Защита банковской тайны:</b> маскирование чувствительных реквизитов и идентификаторов перед отправкой в аналитический контур.</li>
                <li><b>Аудит операций:</b> полное журналирование всех обращений к корпоративному профилю и базе знаний.</li>
                <li><b>Санитизация внешних источников:</b> фильтрация входящего новостного потока и режим Read-Only без права автоматического проведения транзакций.</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with sec_col2:
        st.markdown(
            """
        <div class="block-card">
            <div class="block-title">Контроль качества и обратная связь</div>
            <ul style="font-size:13.5px;line-height:1.65;color:#1D1D1F;padding-left:18px;">
                <li><b>Продуктовые метрики:</b> отслеживание вовлеченности по ролям ЛПР и востребованности банковских инструментов хеджирования.</li>
                <li><b>Автоматическая кросс-проверка:</b> сверка сгенерированных выводов с официальными обзорами Центра макроэкономических исследований Альфа-Банка.</li>
                <li><b>Экспертная калибровка:</b> учет оценок пользователей для динамической подстройки отраслевых весов ОКВЭД.</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )
