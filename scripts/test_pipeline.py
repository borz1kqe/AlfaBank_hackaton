# scripts/test_pipeline.py
from src.services.rag_store import AlfaRAGStore


def run_smoke_test() -> None:
    store = AlfaRAGStore()
    companies = store.context_builder.list_company_ids()
    print(f"Загружено компаний КБ: {len(companies)} -> {companies}\n")

    for u_id in ["U_METAL_001", "U_RETAIL_002", "U_IT_HOLD_005"]:
        ctx = store.get_company_context(u_id)
        print("=" * 80)
        print(f"КОМПАНИЯ: {ctx.synthetic_u} ({ctx.org_type}) | {ctx.main_okved_code} — {ctx.main_okved_name}")
        print(f"Выручка: {ctx.revenue / 1e9:.1f} млрд руб. | Доля в ОКВЭД: {ctx.industry_market_share_pct}% | Позиция: {ctx.market_position_label}")
        print(f"Группа: {ctx.group_context.group_id} ({ctx.group_context.companies_count} комп., выручка группы {ctx.group_context.total_group_revenue / 1e9:.1f} млрд руб.)")
        print(f"Активные продукты: {ctx.active_products}")
        print(f"Потенциал апсейла: {ctx.available_upsell_products}")
        print(f"Топ-контрагенты ({len(ctx.top_counterparties)}):")
        for cp in ctx.top_counterparties:
            print(f"  - [{cp.role.upper()}] {cp.synthetic_u} ({cp.okved_code} {cp.okved_name}): {cp.total_payment_amt / 1e9:.1f} млрд руб. ({cp.share_in_turnover_pct}%)")
        print("Триггеры чувствительности:")
        for rf in ctx.risk_sensitivity_factors:
            print(f"  * {rf}")

        news = store.search_relevant_news(ctx, role="relationship_manager", top_k=3)
        print("\nТоп-3 релевантные новости (прямые + через цепочку поставок):")
        all_triggers = []
        for n in news:
            all_triggers.extend(n.macro_triggers)
            print(f"  -> [{n.news_id}] {n.title} (ОКВЭД: {n.affected_okveds}, Триггеры: {n.macro_triggers})")

        research = store.search_bank_analytics(
            query=f"{ctx.main_okved_name} {' '.join(ctx.risk_sensitivity_factors)}",
            triggers=list(set(all_triggers)),
            top_k=2,
        )
        print("\nПодтверждающие макро-отчеты Альфа-Банка:")
        for r in research:
            print(f"  [Отчет: {r.report_title}] Тезис: {r.key_thesis}")
        print()


if __name__ == "__main__":
    run_smoke_test()
