# -*- coding: utf-8 -*-
import streamlit as st
from mock_data import MOCK_COMPANIES, MOCK_INSIGHTS, CHAT_RESPONSES

st.set_page_config(page_title="Альфа-Инсайт | Интернет-банк", page_icon="🔴", layout="wide")

st.markdown("""
<style>
    body { background-color: #F8F9FA; }
    .alfa-bar { background: #111827; color: white; padding: 12px 20px; border-radius: 10px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;}
    .alfa-logo { background: #EF3124; color: white; padding: 4px 10px; border-radius: 6px; font-weight: 900;}
    .alfa-card { background: white; border-radius: 14px; padding: 20px; border: 1px solid #E5E7EB; margin-bottom: 20px; }
    .badge { background: #FEE2E2; color: #B91C1C; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 0.8rem; }
    .alfa-quote { background: #F0F9FF; border-left: 4px solid #0284C7; padding: 10px 14px; border-radius: 4px; margin-bottom: 10px; }
    .ai-quote { background: #FEF2F2; border-left: 4px solid #EF3124; padding: 10px 14px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="alfa-bar">
    <div><span class="alfa-logo">А</span> <b>АЛЬФА-БИЗНЕС ОНЛАЙН</b></div>
    <div style="color: #9CA3AF;">Сервис «Альфа-Инсайт»</div>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns([2, 1])
with c1:
    comp_names = [c.name for c in MOCK_COMPANIES]
    selected_comp = st.selectbox("Компания:", comp_names)
with c2:
    role = st.selectbox("Роль ЛПР:", ["CFO", "CEO", "TREASURER", "ACCOUNTANT"])

current_comp = next(c for c in MOCK_COMPANIES if c.name == selected_comp)
insights = [i for i in MOCK_INSIGHTS if i.company_id == current_comp.id]

st.markdown(f"### ⚡ Инсайты для {role}")

for ins in insights:
    st.markdown(f"""
    <div class="alfa-card">
        <span class="badge">КРИТИЧНО ДЛЯ ВАШЕГО БИЗНЕСА</span>
        <h2>{ins.title}</h2>
        <p><b>Что произошло:</b> {ins.fact_summary}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_risks, col_opps = st.columns(2)
    with col_risks:
        st.error("**Риски для компании:**\n" + "\n".join([f"• {r}" for r in ins.risks]))
    with col_opps:
        st.success("**Возможности:**\n" + "\n".join([f"• {o}" for o in ins.opportunities]))

    st.markdown("#### Оценка Альфа-Банка vs Вывод ИИ")
    st.markdown(f"""
    <div class="alfa-quote">
        <b>🏛 Позиция аналитиков Альфа-Банка:</b><br>
        «{ins.alfa_view.analyst_quote}»<br>
        <small>Отчет: {ins.alfa_view.report_title}</small>
    </div>
    <div class="ai-quote">
        <b>🤖 Персонализированный AI-вывод:</b><br>
        {ins.ai_inference.custom_forecast}<br>
        <small>Уверенность: {int(ins.ai_inference.confidence_score * 100)}%</small>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"#### Рекомендуемые шаги для {role}:")
    for step in ins.recommended_actions.get(role, []):
        st.checkbox(step, key=f"step_{step}")

    prod = ins.banking_product
    st.info(f"💼 **Решение от Банка:** {prod.product_name} — {prod.description}")
    if st.button(f"🔴 {prod.cta_text}", key="cta"):
        st.balloons()
        st.success("Заявка направлена в Альфа-Банк!")

    with st.expander("🔍 Traceability (Как AI пришел к этому выводу)"):
        for t in ins.traceability:
            st.write(f"**{t.stage}:** {t.detail} (Источник: `{t.source}`)")

    q = st.text_input("Задать уточняющий вопрос AI-аналитику:")
    if st.button("Спросить"):
        st.write(f"🤖 **Ответ:** {CHAT_RESPONSES[default]}")
