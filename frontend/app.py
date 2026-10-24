# -*- coding: utf-8 -*-
"""
Альфа-Инсайт | Интернет-банк «Альфа-Бизнес»
Live AI Multi-Model Router: Контрастная кнопка шторки, Cooldown-защита и 1800 токенов
"""

import streamlit as st
try:
    import streamlit.components.v1 as components
except Exception:
    components = None
import requests
import os
import sys
import time
import base64
import json
import re
import io
from datetime import datetime
from xml.sax.saxutils import escape as xml_escape
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

st.set_page_config(
    page_title="Альфа-Инсайт | Интернет-банк «Альфа-Бизнес»",
    page_icon="https://alfabank.servicecdn.ru/icons/corp/favicons/favicon.ico",
    layout="wide",
    initial_sidebar_state="auto"
)

# Официальные шлюзы и ключи
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

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    #MainMenu, footer, div[data-testid="stStatusWidget"], .viewerBadge_container__1QSob {
        display: none !important;
        visibility: hidden !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 3.5rem !important;
        min-height: 3.5rem !important;
        overflow: visible !important;
    }
    /* правый тулбар Streamlit скрываем, кнопки шторки остаются видимыми */
    [data-testid="stToolbarActions"],
    [data-testid="stAppDeployButton"],
    [data-testid="stMainMenu"] { display: none !important; }

    /* КНОПКА ОТКРЫТИЯ ШТОРКИ: яркая, с подписью, всегда поверх контента */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stExpandSidebarButton"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        position: static !important;
        margin: 0 !important;
        padding: 0 !important;
        transform: none !important;
    }
    [data-testid="stSidebarCollapsedControl"] button,
    button[data-testid="stExpandSidebarButton"] {
        display: inline-flex !important;
        position: fixed !important;
        top: 12px !important;
        left: 14px !important;
        margin: 0 !important;
        z-index: 999999 !important;
        visibility: visible !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        background: linear-gradient(135deg, #EF3124 0%, #C8201A 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 14px !important;
        height: 44px !important;
        min-width: 138px !important;
        padding: 0 18px !important;
        cursor: pointer !important;
        box-shadow: 0 8px 22px rgba(239, 49, 36, 0.35), 0 0 0 4px rgba(239, 49, 36, 0.12) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease !important;
        animation: alfa-pulse 2.8s ease-in-out infinite;
    }
    [data-testid="stSidebarCollapsedControl"] button:hover,
    button[data-testid="stExpandSidebarButton"]:hover {
        transform: translateY(-1px) scale(1.03) !important;
        box-shadow: 0 12px 28px rgba(239, 49, 36, 0.45), 0 0 0 5px rgba(239, 49, 36, 0.18) !important;
    }
    [data-testid="stSidebarCollapsedControl"] button > *,
    button[data-testid="stExpandSidebarButton"] > * {
        display: none !important;
    }
    [data-testid="stSidebarCollapsedControl"] button::before,
    button[data-testid="stExpandSidebarButton"]::before {
        content: "☰";
        font-size: 18px;
        line-height: 1;
        color: #FFFFFF;
    }
    [data-testid="stSidebarCollapsedControl"] button::after,
    button[data-testid="stExpandSidebarButton"]::after {
        content: "Меню банка";
        font-size: 13.5px;
        font-weight: 700;
        letter-spacing: 0.01em;
        color: #FFFFFF;
    }
    @keyframes alfa-pulse {
        0%, 100% { box-shadow: 0 8px 22px rgba(239, 49, 36, 0.35), 0 0 0 4px rgba(239, 49, 36, 0.12); }
        50%      { box-shadow: 0 8px 22px rgba(239, 49, 36, 0.35), 0 0 0 9px rgba(239, 49, 36, 0.05); }
    }

    /* КНОПКА ЗАКРЫТИЯ ШТОРКИ: контрастная, с подписью */
    [data-testid="stSidebarHeader"] {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
        padding: 0.9rem 1rem 0.2rem 1rem !important;
    }
    [data-testid="stSidebarCollapseButton"] button,
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarHeader"] button {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 6px !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: rgba(255, 255, 255, 0.12) !important;
        border: 1px solid rgba(255, 255, 255, 0.30) !important;
        border-radius: 10px !important;
        height: 36px !important;
        width: auto !important;
        min-width: 108px !important;
        padding: 0 14px !important;
        cursor: pointer !important;
        transition: all 0.18s ease !important;
    }
    [data-testid="stSidebarCollapseButton"] button:hover,
    button[data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="stSidebarHeader"] button:hover {
        background: #EF3124 !important;
        border-color: #EF3124 !important;
    }
    [data-testid="stSidebarCollapseButton"] button > *,
    button[data-testid="stSidebarCollapseButton"] > *,
    [data-testid="stSidebarHeader"] button > * {
        display: none !important;
    }
    [data-testid="stSidebarCollapseButton"] button::before,
    button[data-testid="stSidebarCollapseButton"]::before,
    [data-testid="stSidebarHeader"] button::before {
        content: "‹";
        font-size: 22px;
        font-weight: 700;
        line-height: 1;
        color: #FFFFFF;
    }
    [data-testid="stSidebarCollapseButton"] button::after,
    button[data-testid="stSidebarCollapseButton"]::after,
    [data-testid="stSidebarHeader"] button::after {
        content: "Закрыть";
        font-size: 12.5px;
        font-weight: 700;
        color: #FFFFFF;
    }

    /* ШТОРКА (TITANIUM BLACK) */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
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

    /* ЧАТ */
    .chat-bubble-user {
        background: #E5E7EB;
        border-radius: 16px 16px 4px 16px;
        padding: 12px 18px;
        font-size: 0.9rem;
        color: #111827;
        margin: 14px 0 10px auto;
        max-width: 85%;
        width: fit-content;
    }
    .chat-bubble-ai-wrap {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px 16px 16px 4px;
        padding: 18px 22px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 12px;
    }

    /* ПОЛИРОВКА ДИЗАЙНА */
    .stApp {
        background-image: radial-gradient(1100px 420px at 85% -10%, rgba(239, 49, 36, 0.06), transparent 60%),
                          linear-gradient(180deg, #F7F7F9 0%, #EEF0F4 100%) !important;
    }
    @keyframes alfa-fade-up {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .apple-kpi-bar, .apple-hero-banner, .apple-card-panel {
        animation: alfa-fade-up 0.45s ease both;
    }
    .apple-kpi-bar {
        border-radius: 20px;
        box-shadow: 0 6px 24px rgba(17, 24, 39, 0.05);
    }
    .apple-hero-banner {
        background: linear-gradient(100deg, #FFFFFF 0%, #FFF6F5 100%);
        box-shadow: 0 8px 26px rgba(239, 49, 36, 0.08);
    }
    .apple-card-panel {
        border-radius: 22px;
        box-shadow: 0 10px 34px rgba(17, 24, 39, 0.06);
    }
    .apple-subbox, .apple-box-bank, .apple-box-ai, .product-apple-card {
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .apple-subbox:hover, .apple-box-bank:hover, .apple-box-ai:hover, .product-apple-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(17, 24, 39, 0.07);
    }
    .product-apple-card {
        background: linear-gradient(100deg, #FFF8F7 0%, #F9FAFB 100%);
    }
    .apple-tag-pill { border-radius: 980px; padding: 5px 12px; }
    .apple-risk-row, .apple-opp-row { border-radius: 14px; }

    /* Основные действия: красные кнопки */
    [class*="st-key-ask_"] button,
    [class*="st-key-btn_prod_"] button {
        background: linear-gradient(180deg, #FF4B3E 0%, #EF3124 52%, #D3281C 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.28) !important;
        border-radius: 980px !important;
        font-weight: 600 !important;
        letter-spacing: 0.005em !important;
        text-shadow: 0 1px 1px rgba(120, 10, 5, 0.25);
        box-shadow: 0 1px 0 rgba(255, 255, 255, 0.38) inset,
                    0 -1px 0 rgba(0, 0, 0, 0.08) inset,
                    0 8px 20px rgba(239, 49, 36, 0.30),
                    0 2px 5px rgba(239, 49, 36, 0.22) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease !important;
    }
    [class*="st-key-ask_"] button p, [class*="st-key-ask_"] button span,
    [class*="st-key-btn_prod_"] button p, [class*="st-key-btn_prod_"] button span {
        color: #FFFFFF !important;
    }
    [class*="st-key-ask_"] button:hover,
    [class*="st-key-btn_prod_"] button:hover {
        background: linear-gradient(180deg, #FF5B4F 0%, #F23A2D 52%, #DB2D20 100%) !important;
        color: #FFFFFF !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
        transform: translateY(-1px);
        box-shadow: 0 1px 0 rgba(255, 255, 255, 0.45) inset,
                    0 -1px 0 rgba(0, 0, 0, 0.08) inset,
                    0 12px 26px rgba(239, 49, 36, 0.38),
                    0 3px 8px rgba(239, 49, 36, 0.26) !important;
    }
    [class*="st-key-ask_"] button:active,
    [class*="st-key-btn_prod_"] button:active {
        transform: translateY(0) scale(0.98);
        filter: brightness(0.96);
    }
    .chat-bubble-user, .chat-bubble-user * { color: #FFFFFF !important; }
    div.stButton > button:hover { transform: translateY(-1px); }

    /* Поля ввода */
    .stTextInput div[data-baseweb="input"] {
        border: 1px solid #D1D5DB !important;
        background: #FFFFFF !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stTextInput div[data-baseweb="input"]:focus-within {
        border-color: #EF3124 !important;
        box-shadow: 0 0 0 3px rgba(239, 49, 36, 0.14) !important;
    }

    /* Чекбоксы и аудит-лог */
    [data-testid="stCheckbox"] {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 8px 12px;
        margin-bottom: 6px;
    }
    [data-testid="stCheckbox"]:hover { border-color: #EF3124; background: #FFF8F7; }
    [data-testid="stExpander"] {
        border: 1px solid #E5E7EB !important;
        border-radius: 14px !important;
        background: #FFFFFF !important;
    }

    /* Чат */
    .chat-bubble-user {
        background: linear-gradient(135deg, #EF3124 0%, #D42A1E 100%);
        color: #FFFFFF;
        box-shadow: 0 4px 14px rgba(239, 49, 36, 0.22);
    }
    .chat-bubble-ai-wrap {
        border-left: 3px solid #EF3124;
        box-shadow: 0 4px 16px rgba(17, 24, 39, 0.05);
    }

    /* Шторка: навигация и скролл */
    [data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #FFFFFF !important;
    }
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 8px; }

    /* ШРИФТ: San Francisco (иконки Material не трогаем) */
    html, body, .stApp,
    .stApp *:not([data-testid="stIconMaterial"]):not(.material-icons):not(.material-symbols-rounded),
    [data-testid="stSidebar"] *:not([data-testid="stIconMaterial"]) {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", "Inter", "Segoe UI", Roboto, Arial, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        letter-spacing: -0.011em !important;
    }
    .apple-title-h2 { font-size: 1.35rem; letter-spacing: -0.025em !important; }
    div.stButton > button { font-size: 0.88rem !important; }
    [data-testid="stCheckbox"] label { font-size: 0.92rem !important; }

    /* Пустая оболочка карточки создавала белый пустой блок */
    .apple-card-panel:empty { display: none !important; }

    /* Калькулятор свопа и кнопка PDF */
    .swap-box { border-radius: 14px; padding: 14px 16px; border: 1px solid #E5E7EB; background: #F9FAFB; height: 100%; }
    .swap-box.before { border-left: 4px solid #9CA3AF; }
    .swap-box.after  { border-left: 4px solid #0071E3; background: #F8FAFC; }
    .swap-box.save-pos { border-left: 4px solid #16A34A; background: #F6FDF8; }
    .swap-box.save-neg { border-left: 4px solid #DC2626; background: #FFF8F8; }
    .swap-lbl { font-size: 0.72rem; font-weight: 700; color: #6B7280; text-transform: uppercase; letter-spacing: 0.04em; }
    .swap-val { font-size: 1.45rem; font-weight: 700; color: #111827; margin-top: 2px; }
    .swap-sub { font-size: 0.78rem; color: #4B5563; margin-top: 2px; }
    [data-testid="stDownloadButton"] button {
        background: #FFFFFF !important; color: #111827 !important;
        border: 1px solid #D1D5DB !important; border-radius: 980px !important;
        font-weight: 600 !important; min-height: 42px !important; width: 100% !important;
    }
    [data-testid="stDownloadButton"] button:hover { border-color: #EF3124 !important; color: #EF3124 !important; background: #FFF8F7 !important; }

    @media (max-width: 768px) {
        div.block-container {
            padding: 4.6rem 0.6rem 3rem 0.6rem !important;
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

def _build_messages(system_msg: str, context: str, prompt: str, history: list = None) -> list:
    msgs = [{
        "role": "system",
        "content": (
            system_msg
            + "\n4. Это продолжающийся диалог: учитывай предыдущие реплики, не повторяй уже сказанное и развивай расчёт."
            + f"\n\nКонтекст предприятия:\n{context}"
        )
    }]
    for turn in (history or [])[-6:]:
        msgs.append({"role": "user", "content": turn["q"]})
        msgs.append({"role": "assistant", "content": turn["a"]})
    msgs.append({"role": "user", "content": f"Вопрос руководителя:\n{prompt}"})
    return msgs

# ВЫЗОВ МОДЕЛИ С COOLDOWN-ЗАЩИТОЙ И 1800 ТОКЕНАМИ
def call_live_llm(prompt: str, context: str, history: list = None) -> str:
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
        "messages": _build_messages(system_msg, context, prompt, history),
        "temperature": 0.3,
        "max_tokens": 1800
    }
    
    for url in [f"{PRIMARY_URL}/chat/completions", f"{BACKUP_URL}/chat/completions"]:
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=20.0)
            if r.status_code == 200:
                res_data = r.json()
                content = res_data["choices"][0]["message"]["content"]
                if content and len(content.strip()) > 0:
                    return content
        except Exception:
            continue
    return None

def _build_ctx(company: dict, role: str, insight: dict) -> str:
    return (
        f"Компания: {company.get('display_name')}\n"
        f"ОКВЭД: {company.get('main_okved_code')}\n"
        f"Выручка: {company.get('revenue')} руб., Кредитный долг: {company.get('debt_preview')}\n"
        f"Роль руководителя: {role}\n"
        f"Событие: {insight.get('title')}\n"
        f"Позиция Альфа-Банка: {insight.get('alfa_quote')}"
    )

def _offline_answer(question: str) -> str:
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

def ask_ai_chat(company: dict, role: str, insight: dict, question: str, history: list = None) -> str:
    live_result = call_live_llm(question, _build_ctx(company, role, insight), history)
    return live_result if live_result else _offline_answer(question)

# ПОТОКОВЫЙ ВЫВОД: ответ появляется по мере генерации (SSE)
def stream_live_llm(prompt: str, context: str, history: list = None):
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
        "messages": _build_messages(system_msg, context, prompt, history),
        "temperature": 0.3,
        "max_tokens": 1800,
        "stream": True
    }
    for url in [f"{PRIMARY_URL}/chat/completions", f"{BACKUP_URL}/chat/completions"]:
        got = False
        try:
            with requests.post(url, headers=headers, json=payload, stream=True, timeout=(5, 20)) as r:
                if r.status_code != 200:
                    continue
                ctype = r.headers.get("Content-Type", "")
                if "event-stream" not in ctype:
                    # шлюз проигнорировал stream=True и вернул обычный JSON
                    content = r.json()["choices"][0]["message"]["content"]
                    if content and content.strip():
                        yield content
                        return
                    continue
                for raw in r.iter_lines():
                    if not raw:
                        continue
                    line = raw.decode("utf-8", "ignore")
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        delta = json.loads(data)["choices"][0]["delta"].get("content") or ""
                    except Exception:
                        continue
                    if delta:
                        got = True
                        yield delta
            if got:
                return
        except Exception:
            if got:
                return
            continue

def ask_ai_stream(company: dict, role: str, insight: dict, question: str, history: list = None):
    """Генератор для st.write_stream: живой поток от модели, при сбое — заготовленный ответ по словам."""
    produced = False
    for chunk in stream_live_llm(question, _build_ctx(company, role, insight), history):
        produced = True
        yield chunk
    if not produced:
        for tok in re.split(r"(\s+)", _offline_answer(question)):
            if tok:
                yield tok
                time.sleep(0.02)

# КАЛЬКУЛЯТОР СВОПА И ГРАФИКИ
SWAP_SPREAD = 2.1        # спред к ключевой ставке по ГКС №ALF-774, % годовых
SWAP_KEY_RATE = 14.0     # текущая ключевая ставка, %
SWAP_TERM_MONTHS = 24    # срок свопа, мес.

def _fmt(x: float, d: int = 1) -> str:
    return f"{x:,.{d}f}".replace(",", " ")

def _rate_scenarios() -> "pd.DataFrame":
    """Иллюстративные сценарии ключевой ставки на 2027 г. (базовый откалиброван на средний прогноз Альфа-Банка 12.5%)."""
    months = pd.date_range("2027-01-01", periods=12, freq="MS")
    base = [13.7 - i * (2.4 / 11) for i in range(12)]    # среднее ≈ 12.5
    soft = [13.3 - i * (3.6 / 11) for i in range(12)]    # мягкий: ≈ 11.5
    hard = [14.0 + i * (1.0 / 11) for i in range(12)]    # жёсткий: ≈ 14.5
    return pd.DataFrame({"Базовый (прогноз Альфа-Банка)": base, "Мягкий": soft, "Жёсткий": hard}, index=months)

def compute_swap(amount_bn: float, swap_rate: float) -> dict:
    amt_mln = amount_bn * 1000.0
    before_year = amt_mln * (SWAP_KEY_RATE + SWAP_SPREAD) / 100.0
    after_year = amt_mln * (swap_rate + SWAP_SPREAD) / 100.0
    save_year = before_year - after_year
    sc = _rate_scenarios()
    sc_cost = {name: amt_mln * (sc[name].mean() + SWAP_SPREAD) / 100.0 for name in sc.columns}
    return {
        "amount_bn": amount_bn, "swap_rate": swap_rate,
        "before_year": before_year, "after_year": after_year,
        "before_month": before_year / 12, "after_month": after_year / 12,
        "save_year": save_year, "save_month": save_year / 12,
        "save_term": save_year * SWAP_TERM_MONTHS / 12,
        "irs_cost_2027": after_year, "sc_cost": sc_cost,
    }

def render_swap_calculator(ins: dict) -> dict:
    st.markdown(
        '<div style="font-size:0.92rem;font-weight:700;color:#111827;margin:18px 0 4px 0;">Калькулятор процентного свопа (IRS)</div>'
        f'<div style="font-size:0.8rem;color:#6B7280;margin-bottom:8px;">Формула: сумма × (ставка + спред {SWAP_SPREAD}%) ÷ 12. '
        f'Сравнение с текущей ключевой {SWAP_KEY_RATE}%, срок {SWAP_TERM_MONTHS} мес.</div>',
        unsafe_allow_html=True
    )
    s1, s2 = st.columns(2)
    with s1:
        amount_bn = st.slider("Сумма транша, млрд ₽", 0.5, 24.8, 5.0, 0.1, key=f"swap_amt_{ins['id']}")
    with s2:
        swap_rate = st.slider("Фиксированная ставка свопа, %", 9.0, 16.0, 12.6, 0.1, key=f"swap_rate_{ins['id']}")
    r = compute_swap(amount_bn, swap_rate)

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(
            '<div class="swap-box before"><div class="swap-lbl">До: плавающая ставка</div>'
            f'<div class="swap-val">{_fmt(r["before_month"], 2)} млн ₽/мес</div>'
            f'<div class="swap-sub">КС {SWAP_KEY_RATE}% + {SWAP_SPREAD}% = {_fmt(SWAP_KEY_RATE + SWAP_SPREAD)}% • {_fmt(r["before_year"])} млн ₽/год</div></div>',
            unsafe_allow_html=True)
    with k2:
        st.markdown(
            '<div class="swap-box after"><div class="swap-lbl">После: IRS</div>'
            f'<div class="swap-val">{_fmt(r["after_month"], 2)} млн ₽/мес</div>'
            f'<div class="swap-sub">{_fmt(swap_rate)}% + {SWAP_SPREAD}% = {_fmt(swap_rate + SWAP_SPREAD)}% • {_fmt(r["after_year"])} млн ₽/год</div></div>',
            unsafe_allow_html=True)
    with k3:
        pos = r["save_year"] >= 0
        sign = "Экономия" if pos else "Переплата"
        st.markdown(
            f'<div class="swap-box {"save-pos" if pos else "save-neg"}"><div class="swap-lbl">{sign} (при КС {SWAP_KEY_RATE}%)</div>'
            f'<div class="swap-val">{_fmt(abs(r["save_year"]))} млн ₽/год</div>'
            f'<div class="swap-sub">{_fmt(abs(r["save_month"]), 2)} млн ₽/мес • {_fmt(abs(r["save_term"]))} млн ₽ за {SWAP_TERM_MONTHS} мес.</div></div>',
            unsafe_allow_html=True)

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    g1, g2 = st.columns(2)
    sc = _rate_scenarios()
    with g1:
        st.caption("КЛЮЧЕВАЯ СТАВКА НА 2027 ГОД ПО СЦЕНАРИЯМ, %")
        line_df = sc.copy()
        line_df["Фикс. по IRS"] = swap_rate
        st.line_chart(line_df, color=["#0071E3", "#16A34A", "#DC2626", "#EF3124"], height=260)
    with g2:
        st.caption(f"СТОИМОСТЬ ОБСЛУЖИВАНИЯ ТРАНША В 2027 Г., МЛН ₽")
        order = [("1 Мягкий", "Мягкий"), ("2 Базовый", "Базовый (прогноз Альфа-Банка)"), ("3 Жёсткий", "Жёсткий")]
        bar_df = pd.DataFrame({
            "Без хеджа": [r["sc_cost"][k] for _, k in order],
            "С IRS": [r["irs_cost_2027"]] * 3,
        }, index=[lbl for lbl, _ in order])
        st.bar_chart(bar_df, color=["#9CA3AF", "#EF3124"], height=260)
    d = {lbl: r["sc_cost"][k] - r["irs_cost_2027"] for lbl, k in order}
    st.caption(
        "Иллюстративные сценарии; базовый откалиброван на средний прогноз Альфа-Банка 12.5% на 2027 г. "
        f"Выигрыш IRS против плавающей ставки в 2027 г.: мягкий {_fmt(d['1 Мягкий'])}, базовый {_fmt(d['2 Базовый'])}, "
        f"жёсткий {_fmt(d['3 Жёсткий'])} млн ₽ (отрицательное значение — своп дороже). Своп страхует от жёсткого сценария."
    )
    return r

# PDF-СПРАВКА ДЛЯ РУКОВОДИТЕЛЯ (1 страница)
def _find_pdf_fonts():
    base = Path(__file__).resolve().parent
    pairs = [
        (base / "fonts" / "DejaVuSans.ttf", base / "fonts" / "DejaVuSans-Bold.ttf"),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
        (Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf")),
        (Path("/usr/share/fonts/TTF/DejaVuSans.ttf"), Path("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf")),
        (Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"), Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")),
        (Path("/Library/Fonts/Arial.ttf"), Path("/Library/Fonts/Arial Bold.ttf")),
        (Path("/System/Library/Fonts/Supplemental/Arial.ttf"), Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")),
        (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")),
    ]
    for reg, bold in pairs:
        if reg.exists():
            return reg, (bold if bold.exists() else reg)
    return None, None

def build_cfo_brief_pdf(company: dict, role: str, ins: dict, swap: dict = None):
    """Возвращает bytes PDF (одна страница A4) или None, если нет reportlab / кириллического шрифта."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepInFrame
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except Exception:
        return None
    reg, bold = _find_pdf_fonts()
    if reg is None:
        return None
    try:
        pdfmetrics.registerFont(TTFont("AlfaSans", str(reg)))
        pdfmetrics.registerFont(TTFont("AlfaSans-Bold", str(bold)))
    except Exception:
        return None

    red = colors.HexColor("#EF3124")
    grey = colors.HexColor("#6B7280")
    e = xml_escape
    body = ParagraphStyle("b", fontName="AlfaSans", fontSize=9.5, leading=13, textColor=colors.HexColor("#111827"))
    small = ParagraphStyle("s", parent=body, fontSize=8, leading=10.5, textColor=grey)
    lbl = ParagraphStyle("l", parent=body, fontName="AlfaSans-Bold", fontSize=9, textColor=red)
    h1 = ParagraphStyle("h1", parent=body, fontName="AlfaSans-Bold", fontSize=15, leading=19)
    title = ParagraphStyle("t", parent=body, fontName="AlfaSans-Bold", fontSize=11.5, leading=15)

    def P(text, style=body):
        return Paragraph(text, style)

    risks = [P("• " + e(r_)) for r_ in ins["risks"]]
    actions = [P(f"{i}. " + e(a_)) for i, a_ in enumerate(ins["actions"], 1)]
    event = [P(e(ins["title"]), title), Spacer(1, 2), P(e(ins["facts"])),
             Spacer(1, 2), P(f"{e(ins['date'])} • Источник: {e(ins['source'])}", small)]
    product = [P(e(ins["prod_title"]), title), Spacer(1, 2), P(e(ins["prod_desc"]))]
    if swap:
        sign = "Экономия" if swap["save_year"] >= 0 else "Переплата"
        product += [Spacer(1, 4), P(
            f"<b>Расчёт IRS:</b> транш {_fmt(swap['amount_bn'])} млрд ₽, фикс. ставка {_fmt(swap['swap_rate'])}%, срок {SWAP_TERM_MONTHS} мес. "
            f"Платёж до: {_fmt(swap['before_month'], 2)} млн ₽/мес, после: {_fmt(swap['after_month'], 2)} млн ₽/мес. "
            f"{sign} при КС {SWAP_KEY_RATE}%: {_fmt(abs(swap['save_year']))} млн ₽/год.")]

    rows = [
        [P("СОБЫТИЕ", lbl), event],
        [P("РИСК", lbl), risks],
        [P("ДЕЙСТВИЕ", lbl), actions],
        [P("ПРОДУКТ БАНКА", lbl), product],
    ]
    tbl = Table(rows, colWidths=[34 * mm, 146 * mm])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#E5E7EB")),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))

    story = [
        P("Альфа-Инсайт • Краткая справка для руководителя", h1),
        Spacer(1, 3),
        P(f"{e(company.get('display_name', ''))} • Роль: {e(role)} • Сформировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}", small),
        Spacer(1, 8), tbl, Spacer(1, 10),
        P("Справка сформирована AI-ассистентом на основе открытых источников и данных клиента. "
          "Расчёты ориентировочные и не являются офертой; решение принимает уполномоченный сотрудник.", small),
    ]
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm,
                            title="Справка Альфа-Инсайт", author="Альфа-Инсайт")
    frame = KeepInFrame(180 * mm, 267 * mm, story, mode="shrink")  # гарантирует одну страницу
    doc.build([frame])
    return buf.getvalue()

def brief_as_text(company: dict, role: str, ins: dict) -> str:
    return (
        f"АЛЬФА-ИНСАЙТ: КРАТКАЯ СПРАВКА\n{company.get('display_name')} • {role}\n\n"
        f"СОБЫТИЕ: {ins['title']}\n{ins['facts']}\n\nРИСК:\n" + "\n".join("- " + r for r in ins["risks"]) +
        "\n\nДЕЙСТВИЕ:\n" + "\n".join(f"{i}. {a}" for i, a in enumerate(ins["actions"], 1)) +
        f"\n\nПРОДУКТ: {ins['prod_title']}\n{ins['prod_desc']}\n"
    )

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "applied_products" not in st.session_state:
    st.session_state.applied_products = set()
if "last_api_call" not in st.session_state:
    st.session_state.last_api_call = 0.0

# Streamlit удаляет состояние виджетов, которые не отрисованы в текущем прогоне
# (например, при переходе на другую вкладку шторки). Переприсваивание делает значения
# обычными данными сессии, поэтому введённый запрос и отмеченные шаги не сбрасываются.
for _k in list(st.session_state.keys()):
    if isinstance(_k, str) and _k.startswith(("inp_", "step_", "swap_")):
        st.session_state[_k] = st.session_state[_k]

# ШТОРКА
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
    st.markdown(f"<div style='font-size:0.75rem;color:#9CA3AF;'>Модель: <b>{LLM_MODEL.split('/')[-1]}</b><br>Лимит: <b>1800 токенов (Safe)</b></div>", unsafe_allow_html=True)

# ЗАПАСНАЯ КНОПКА ОТКРЫТИЯ ШТОРКИ (появляется, только когда шторка свёрнута)
_SIDEBAR_BTN_JS = """
<script>
(function () {
  var doc;
  try { doc = window.parent.document; } catch (e) { return; }
  var old = doc.getElementById('alfa-open-sidebar');
  if (old) old.remove();

  var btn = doc.createElement('button');
  btn.id = 'alfa-open-sidebar';
  btn.type = 'button';
  btn.innerHTML = '<span style="font-size:18px;line-height:1;">&#9776;</span><span>Меню банка</span>';
  btn.style.cssText = [
    'position:fixed', 'top:12px', 'left:14px', 'z-index:2147483000',
    'display:none', 'align-items:center', 'gap:8px',
    'height:44px', 'padding:0 18px', 'border:none', 'border-radius:14px',
    'cursor:pointer', 'color:#fff', 'font-size:14px', 'font-weight:700',
    'font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Helvetica Neue",Inter,Arial,sans-serif',
    'background:linear-gradient(180deg,#FF4B3E 0%,#EF3124 55%,#D3281C 100%)',
    'box-shadow:0 8px 22px rgba(239,49,36,.38),0 0 0 4px rgba(239,49,36,.14)'
  ].join(';');

  btn.addEventListener('click', function () {
    var el = doc.querySelector('[data-testid="stExpandSidebarButton"]')
          || doc.querySelector('[data-testid="stSidebarCollapsedControl"] button')
          || doc.querySelector('[data-testid="collapsedControl"] button');
    if (el) { el.click(); }
  });
  doc.body.appendChild(btn);

  function refresh() {
    var sb = doc.querySelector('[data-testid="stSidebar"]');
    var collapsed = !sb || sb.getAttribute('aria-expanded') === 'false';
    btn.style.display = collapsed ? 'inline-flex' : 'none';
  }
  refresh();
  setInterval(refresh, 300);
})();
</script>
"""

with st.sidebar:
    if hasattr(st, "iframe"):
        st.iframe(_SIDEBAR_BTN_JS, height=1)
    elif components is not None:
        components.html(_SIDEBAR_BTN_JS, height=0)

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

        swap_res = None
        if ins["id"] == "ins_cbr_1001":
            swap_res = render_swap_calculator(ins)

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
        with col_btn_right:
            pdf_bytes = build_cfo_brief_pdf(current_company, selected_role_label, ins, swap_res)
            if pdf_bytes:
                st.download_button("Скачать краткую справку (PDF)", data=pdf_bytes,
                                   file_name=f"alfa_insight_{ins['id']}.pdf", mime="application/pdf",
                                   key=f"pdf_{ins['id']}")
            else:
                st.download_button("Скачать краткую справку (TXT)", data=brief_as_text(current_company, selected_role_label, ins),
                                   file_name=f"alfa_insight_{ins['id']}.txt", mime="text/plain",
                                   key=f"txt_{ins['id']}")
                st.caption("Для PDF: pip install reportlab и шрифт DejaVuSans в папке fonts/")

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        with st.expander("Аудит-лог и происхождение выводов (Traceability)"):
            st.caption("Пошаговый протокол рассуждения многошагового агента:")
            for t in ins["trace"]:
                st.markdown(f"• {t}")

        st.markdown("<hr style='border:none;border-top:1px solid #E5E7EB;margin:20px 0;'>", unsafe_allow_html=True)

        # Переписка выводится над полем ввода; контейнер наполняется после обработки вопроса
        hist_box = st.container()

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

        inp_key = f"inp_{ins['id']}"
        send_key = f"send_{ins['id']}"
        # очистка поля после отправки (должна произойти до создания виджета)
        if st.session_state.pop(f"clear_{ins['id']}", False):
            st.session_state[inp_key] = ""

        def _on_enter(k=send_key):
            st.session_state[k] = True

        col_input, col_submit = st.columns([4.2, 1])
        with col_input:
            u_query = st.text_input("Вопрос", key=inp_key, placeholder="Задайте следующий вопрос: о ликвидности, кредитах или ВЭД...", label_visibility="collapsed", on_change=_on_enter)
        with col_submit:
            ask_clicked = st.button("Спросить", key=f"ask_{ins['id']}")

        enter_pressed = st.session_state.pop(send_key, False)

        history = st.session_state.chat_history.get(ins['id'], [])
        if isinstance(history, dict):  # совместимость со старым форматом (одна пара вопрос-ответ)
            history = [history]
        st.session_state.chat_history[ins['id']] = history

        pending_q = None
        if ask_clicked or selected_preset or enter_pressed:
            txt = selected_preset if selected_preset else (u_query or "").strip()
            if txt:
                pending_q = txt
                st.session_state.last_api_call = time.time()

        with hist_box:
            for h in history:
                st.markdown(f'<div class="chat-bubble-user"><b>Вы:</b> {h["q"]}</div>', unsafe_allow_html=True)
                with st.container(border=True):
                    st.markdown(h["a"])
            if pending_q:
                st.markdown(f'<div class="chat-bubble-user"><b>Вы:</b> {pending_q}</div>', unsafe_allow_html=True)
                with st.container(border=True):
                    ans = st.write_stream(ask_ai_stream(current_company, selected_role_label, ins, pending_q, history))
                history.append({"q": pending_q, "a": ans})
                if not selected_preset:
                    st.session_state[f"clear_{ins['id']}"] = True
                    st.rerun()
            if history:
                if st.button("Очистить диалог", key=f"clr_{ins['id']}"):
                    st.session_state.chat_history[ins['id']] = []
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<center style='color:#9CA3AF;font-size:0.8rem;margin-top:20px;'>Интернет-банк «Альфа-Бизнес» &nbsp;•&nbsp; Сервис «Альфа-Инсайт»</center>", unsafe_allow_html=True)
