# -*- coding: utf-8 -*-
import streamlit as st
import base64
from pathlib import Path
from mock_data import MOCK_COMPANIES, MOCK_INSIGHTS, CHAT_RESPONSES

st.set_page_config(
    page_title="Альфа-Инсайт | Интернет-банк «Альфа-Бизнес»",
    page_icon="https://alfabank.servicecdn.ru/icons/corp/favicons/favicon.ico",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# SF Symbols & Apple-style Monoline Vector Icons (1.5px stroke)
ICONS = {
    "sparkles": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EF3124" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:6px;"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>',
    "bank": '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:6px;"><rect width="20" height="4" x="2" y="3" rx="1"/><path d="M4 7v11"/><path d="M8 7v11"/><path d="M12 7v11"/><path d="M16 7v11"/><path d="M20 7v11"/><rect width="20" height="3" x="2" y="18" rx="1"/></svg>',
    "shield_alert": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#E11D48" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:6px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "arrow_up_right": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#16A34A" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:6px;"><path d="M7 7h10v10"/><path d="M7 17 17 7"/></svg>',
    "tag": '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#6E6E73" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-1px;margin-right:4px;"><path d="M12 2H2v10l9.29 9.29a2.41 2.41 0 0 0 3.42 0l6.58-6.58a2.41 2.41 0 0 0 0-3.42L12 2Z"/><circle cx="7" cy="7" r="1.5"/></svg>',
    "message": '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#1D1D1F" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:6px;"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "building": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#86868B" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px;"><rect width="16" height="20" x="4" y="2" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M8 10h.01"/><path d="M16 10h.01"/><path d="M8 14h.01"/><path d="M16 14h.01"/></svg>',
    "person": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#86868B" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px;"><circle cx="12" cy="8" r="4"/><path d="M20 21a8 8 0 0 0-16 0"/></svg>'
}

def get_logo_html() -> str:
    svg_file = Path("alfa-bank-business.svg")
    if svg_file.exists():
        svg_content = svg_file.read_text(encoding="utf-8")
        b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
        return f'<img src="data:image/svg+xml;base64,{b64}" height="28" style="vertical-align:middle;margin-right:12px;" />'
    return '<span style="background:#EF3124;color:white;padding:4px 10px;border-radius:8px;font-weight:700;font-size:0.9rem;margin-right:10px;">АЛЬФА</span>'

# Apple Human Interface Guidelines Custom CSS
st.markdown("""
<style>
    /* Прячем служебные элементы Streamlit */
    header, #MainMenu, footer { visibility: hidden; height: 0; }
    div.block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 1180px !important;
    }

    /* Apple Canvas Background & Typography */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", Arial, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        color: #1D1D1F;
        background-color: #F5F5F7;
        letter-spacing: -0.016em;
    }

    /* Navigation Bar (Glassmorphic dark titanium) */
    .apple-nav {
        background: rgba(29, 29, 31, 0.92);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        color: #FFFFFF;
        padding: 14px 28px;
        border-radius: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    }
    .apple-nav-title {
        font-weight: 600;
        font-size: 1.05rem;
        letter-spacing: -0.02em;
    }
    .apple-nav-badge {
        font-size: 0.75rem;
        color: #86868B;
        background: rgba(255, 255, 255, 0.08);
        padding: 4px 10px;
        border-radius: 20px;
        letter-spacing: 0;
    }

    /* Controls Panel Card */
    .apple-controls-card {
        background: #FFFFFF;
        border: 1px solid rgba(0, 0, 0, 0.04);
        border-radius: 18px;
        padding: 16px 22px;
        margin-bottom: 24px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
    }

    /* Entry Point Banner */
    .apple-hero-widget {
        background: #FFFFFF;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 20px;
        padding: 24px 28px;
        margin-bottom: 28px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
        position: relative;
        overflow: hidden;
    }
    .apple-hero-widget::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: #EF3124;
    }

    /* Insight Card */
    .apple-card {
        background: #FFFFFF;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 22px;
        padding: 28px 32px;
        margin-bottom: 28px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    }

    /* Pills & Badges */
    .apple-pill-critical {
        background: #FFF1F2;
        color: #E11D48;
        padding: 4px 12px;
        border-radius: 980px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        display: inline-block;
    }
    .apple-tag {
        background: #F5F5F7;
        color: #424245;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
        margin-right: 8px;
        margin-bottom: 8px;
        border: 1px solid rgba(0, 0, 0, 0.03);
    }

    /* Macro vs AI Cards */
    .apple-split-box {
        border-radius: 16px;
        padding: 20px 22px;
        height: 100%;
    }
    .apple-box-bank {
        background: #F0F7FF;
        border: 1px solid rgba(0, 113, 227, 0.12);
    }
    .apple-box-ai {
        background: #FFF5F5;
        border: 1px solid rgba(239, 49, 36, 0.12);
    }

    /* Risk & Opportunity Item */
    .apple-list-item {
        background: #FAFAFC;
        border: 1px solid rgba(0, 0, 0, 0.04);
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 8px;
        color: #1D1D1F;
    }

    /* Dark Titanium Banking Offer Banner */
    .apple-product-banner {
        background: #1D1D1F;
        color: #FFFFFF;
        border-radius: 18px;
        padding: 24px 28px;
        margin-top: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Buttons */
    div.stButton > button {
        background-color: #EF3124 !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        padding: 10px 22px !important;
        box-shadow: 0 2px 8px rgba(239, 49, 36, 0.2) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div.stButton > button:hover {
        transform: scale(1.01) !important;
        box-shadow: 0 4px 14px rgba(239, 49, 36, 0.3) !important;
    }

    /* Streamlit Form Cleanups */
    div[data-baseweb="select"] {
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "applied_products" not in st.session_state:
    st.session_state.applied_products = set()

# Apple Navigation Bar
logo_html = get_logo_html()
st.markdown(f"""
<div class="apple-nav">
    <div style="display:flex;align-items:center;">
        {logo_html}
        <span class="apple-nav-title">БИЗНЕС ОНЛАЙН</span>
    </div>
    <div class="apple-nav-badge">
        Контур персонализированной аналитики &nbsp;|&nbsp; alfa-hack-2026
    </div>
</div>
""", unsafe_allow_html=True)

# Controls Card: Company & Executive Role
comp_dict = {f"{c.name} ({c.synthetic_u})": c for c in MOCK_COMPANIES}

st.markdown('<div class="apple-controls-card">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([2.5, 2, 1.5])

with c1:
    st.markdown(f"<span style='font-size:0.8rem;color:#86868B;'>{ICONS['building']} КОРПОРАТИВНЫЙ КЛИЕНТ</span>", unsafe_allow_html=True)
    selected_comp_name = st.selectbox("Клиент", list(comp_dict.keys()), label_visibility="collapsed")
    comp = comp_dict[selected_comp_name]

with c2:
    st.markdown(f"<span style='font-size:0.8rem;color:#86868B;'>{ICONS['person']} РОЛЬ ЛПР (СЛАЙД 5)</span>", unsafe_allow_html=True)
    role_map = {
        "CFO": "Финансовый директор (CFO)",
        "CEO": "Генеральный директор (CEO)",
        "TREASURER": "Руководитель казначейства (TREASURER)",
        "ACCOUNTANT": "Главный бухгалтер (ACCOUNTANT)"
    }
    selected_role_label = st.selectbox("Роль", list(role_map.values()), index=0, label_visibility="collapsed")
    role_code = [k for k, v in role_map.items() if v == selected_role_label][0]

with c3:
    st.metric(
        label="Выручка (REVENUE)",
        value=f"{comp.revenue_company:,.0f} млн ₽".replace(",", " "),
        delta="Крупный бизнес (>15 млрд)"
    )
st.markdown('</div>', unsafe_allow_html=True)

# Entry Point Hero Widget (Criterion 09)
insights = [i for i in MOCK_INSIGHTS if i.company_id == comp.synthetic_u]
if not insights:
    insights = [MOCK_INSIGHTS[0]]

st.markdown(f"""
<div class="apple-hero-widget">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <div style="font-size:1.15rem;font-weight:600;color:#1D1D1F;display:flex;align-items:center;">
            {ICONS['sparkles']} Альфа-Инсайт &nbsp;<span style="color:#86868B;font-weight:400;font-size:1rem;">| &nbsp;Интеллектуальный радар событий</span>
        </div>
        <span class="apple-pill-critical">Критичных событий: {len(insights)}</span>
    </div>
    <div style="color:#515154;font-size:0.92rem;line-height:1.5;">
        Система отфильтровала 1 420 внешних публикаций и макро-отчетов Альфа-Банка. 
        Сформирован персональный анализ для роли <b>{selected_role_label}</b> предприятия <b>{comp.name}</b> 
        (ОКВЭД <code>{comp.mainokved_code}</code>, профиль ВЭД: <i>{comp.fts_country_name}</i>).
    </div>
</div>
""", unsafe_allow_html=True)

# Insight Cards (All 6 blocks from Slide 14)
for ins in insights:
    st.markdown(f"""
    <div class="apple-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <span class="apple-pill-critical">Высокий приоритет</span>
            <span style="font-size:0.82rem;color:#86868B;">
                {ins.publish_date} &nbsp;•&nbsp; Источник: <b style="color:#1D1D1F;">{ins.source_name}</b>
            </span>
        </div>
        <div style="font-size:1.4rem;font-weight:700;color:#1D1D1F;line-height:1.35;margin-bottom:20px;letter-spacing:-0.02em;">
            {ins.title}
        </div>
    """, unsafe_allow_html=True)

    # Block 1 & 2
    col_fact, col_why = st.columns(2)
    with col_fact:
        st.markdown("<div style='font-size:0.82rem;font-weight:600;color:#86868B;text-transform:uppercase;margin-bottom:8px;'>1. Что произошло (факты)</div>", unsafe_allow_html=True)
        st.info(f"{ins.fact_summary}\n\n[Официальный первоисточник релиза]({ins.source_url})")

    with col_why:
        st.markdown("<div style='font-size:0.82rem;font-weight:600;color:#86868B;text-transform:uppercase;margin-bottom:8px;'>2. Почему это важно компании</div>", unsafe_allow_html=True)
        tags_html = "".join([f'<span class="apple-tag">{ICONS["tag"]}{t}</span>' for t in ins.triggers])
        st.markdown(tags_html, unsafe_allow_html=True)
        st.warning(f"**Цепочка контрагентов:** {ins.counterparty_impact}")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # Block 3: Consequences (Risks vs Opportunities)
    st.markdown("<div style='font-size:0.82rem;font-weight:600;color:#86868B;text-transform:uppercase;margin-bottom:12px;'>3. Прогноз последствий для бизнеса</div>", unsafe_allow_html=True)
    r_col, o_col = st.columns(2)
    with r_col:
        st.markdown(f"<div style='font-weight:600;color:#E11D48;margin-bottom:8px;'>{ICONS['shield_alert']} Риски</div>", unsafe_allow_html=True)
        for r in ins.risks:
            st.markdown(f'<div class="apple-list-item">{r}</div>', unsafe_allow_html=True)
    with o_col:
        st.markdown(f"<div style='font-weight:600;color:#16A34A;margin-bottom:8px;'>{ICONS['arrow_up_right']} Возможности</div>", unsafe_allow_html=True)
        for o in ins.opportunities:
            st.markdown(f'<div class="apple-list-item">{o}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # Block 4: Alfa Bank Expert Stance vs AI Inference (Criterion 03)
    st.markdown("<div style='font-size:0.82rem;font-weight:600;color:#86868B;text-transform:uppercase;margin-bottom:12px;'>4. Оценка Альфа-Банка vs Вывод AI-модели</div>", unsafe_allow_html=True)
    m_col, ai_col = st.columns(2)
    with m_col:
        st.markdown(f"""
        <div class="apple-split-box apple-box-bank">
            <div style="font-weight:600;color:#0071E3;font-size:0.92rem;margin-bottom:8px;">
                {ICONS['bank']} Позиция аналитиков Альфа-Банка
            </div>
            <div style="font-size:0.9rem;line-height:1.45;color:#1D1D1F;margin-bottom:10px;">
                «{ins.alfa_view.analyst_quote}»
            </div>
            <div style="font-size:0.78rem;color:#6E6E73;">
                Материал: <b>{ins.alfa_view.report_title}</b> ({ins.alfa_view.report_date})<br>
                Базовый сценарий: {ins.alfa_view.alfa_base_forecast}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ai_col:
        st.markdown(f"""
        <div class="apple-split-box apple-box-ai">
            <div style="font-weight:600;color:#EF3124;font-size:0.92rem;margin-bottom:8px;">
                {ICONS['sparkles']} Персонализированный AI-вывод для {comp.name}
            </div>
            <div style="font-size:0.9rem;line-height:1.45;color:#1D1D1F;margin-bottom:10px;">
                {ins.ai_inference.custom_forecast}
            </div>
            <div style="font-size:0.78rem;color:#86868B;">
                Уверенность модели: <b style="color:#1D1D1F;">{int(ins.ai_inference.confidence_score * 100)}%</b> &nbsp;|&nbsp; 
                Драйвер: {ins.ai_inference.primary_driver}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # Block 5: Actions checklist & Banking Product
    st.markdown(f"<div style='font-size:0.82rem;font-weight:600;color:#86868B;text-transform:uppercase;margin-bottom:10px;'>5. Рекомендуемые действия для роли: {selected_role_label}</div>", unsafe_allow_html=True)
    for s_idx, act in enumerate(ins.recommended_actions.get(role_code, []), 1):
        st.checkbox(f"Шаг {s_idx}: {act}", key=f"step_{ins.id}_{s_idx}")

    # Native Banking Product Banner
    prod = ins.banking_product
    st.markdown(f"""
    <div class="apple-product-banner">
        <div>
            <span style="background:#EF3124;color:white;padding:3px 8px;border-radius:6px;font-size:0.7rem;font-weight:600;letter-spacing:0.02em;">
                {prod.badge}
            </span>
            <div style="font-size:1.15rem;font-weight:600;margin-top:6px;">{prod.product_name}</div>
            <div style="font-size:0.85rem;color:#A1A1A6;margin-top:4px;max-width:680px;line-height:1.4;">
                {prod.description}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if ins.id in st.session_state.applied_products:
        st.success(f"Заявка на продукт «{prod.product_name}» направлена корпоративному банкиру Альфа-Банка.")
    else:
        if st.button(f"{prod.cta_text}", key=f"cta_{ins.id}"):
            st.session_state.applied_products.add(ins.id)
            st.balloons()
            st.rerun()

    # Block 6: Traceability log (Criterion 12)
    with st.expander("На чем основан вывод? (Traceability & Агентный протокол)"):
        for t in ins.traceability:
            st.markdown(f"**{t.stage}:** {t.detail} &nbsp;<span style='color:#86868B;font-size:0.8rem;'>(Источник: <code>{t.source}</code>)</span>", unsafe_allow_html=True)

    # Interactive Chat (Criterion 10)
    st.markdown("<hr style='border:none;border-top:1px solid #E5E5EA;margin:24px 0;'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.95rem;font-weight:600;color:#1D1D1F;margin-bottom:10px;'>{ICONS['message']} Задать уточняющий вопрос AI-аналитику</div>", unsafe_allow_html=True)

    q1, q2 = st.columns(2)
    selected_preset = None
    if q1.button("Влияние на долговую нагрузку (CFO)", key=f"p1_{ins.id}"):
        selected_preset = "долговую нагрузку"
    if q2.button("Влияние на цепочку покупателей", key=f"p2_{ins.id}"):
        selected_preset = "поставщиках"

    user_query = st.text_input("Введите вопрос аналитику:", key=f"inp_{ins.id}", placeholder="Например: 'Какой буфер ликвидности потребуется до конца года?'")

    if st.button("Отправить запрос", key=f"ask_{ins.id}") or selected_preset:
        query_text = selected_preset if selected_preset else user_query
        if query_text:
            ans = CHAT_RESPONSES.get(selected_preset, CHAT_RESPONSES["default"])
            st.session_state.chat_history[ins.id] = {"q": query_text, "a": ans}

    if ins.id in st.session_state.chat_history:
        h = st.session_state.chat_history[ins.id]
        st.markdown(f"<div style='background:#F5F5F7;padding:12px 16px;border-radius:12px;margin:12px 0 8px 0;font-size:0.9rem;'><b>Запрос:</b> {h['q']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:#FFFFFF;border:1px solid #E5E5EA;padding:16px 18px;border-radius:14px;font-size:0.92rem;line-height:1.5;'>{h['a']}</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center style='color:#86868B;font-size:0.8rem;margin-top:20px;'>Интернет-банк «Альфа-Бизнес» &nbsp;•&nbsp; Демо-контур alfa-hack-2026</center>", unsafe_allow_html=True)
