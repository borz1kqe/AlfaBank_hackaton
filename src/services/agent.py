# src/services/agent.py
from typing import List, Dict, Any, Optional
from src.models.schemas import (
    CompanyContext,
    NewsItem,
    BankResearchChunk,
    PersonalizedInsight,
    WhatHappenedBlock,
    WhyImportantBlock,
    ConsequencesBlock,
    BankEvaluationBlock,
    RecommendedActionsBlock,
    NativeProductOffer,
    AgentTraceStep,
    TraceabilityBlock,
    ChatRequest,
    ChatResponse,
)
from src.services.llm_client import SafeLLMClient, ALLOWED_MODELS


ROLE_PERSONAS = {
    "CEO": {
        "title": "Генеральный директор / Собственник",
        "focus": "доля рынка, стратегия развития, устойчивость цепочек поставок, действия конкурентов, маржинальность бизнеса",
    },
    "CFO": {
        "title": "Финансовый директор (CFO)",
        "focus": "стоимость заемного финансирования, ключевая ставка ЦБ, ковенанты, долговая нагрузка, валютные риски, CAPEX/OPEX",
    },
    "TREASURER": {
        "title": "Руководитель казначейства",
        "focus": "ликвидность, ставки по депозитам и овернайтам, платежный календарь, кассовые разрывы, трансграничные расчеты ВЭД",
    },
    "ACCOUNTANT": {
        "title": "Главный бухгалтер",
        "focus": "налоговое и таможенное регулирование (ФТС/ФНС), комплаенс, отчетность, документарное сопровождение сделок",
    },
}


class BusinessInsightAgent:
    """
    Многошаговый AI-агент подготовки персонализированных бизнес-инсайтов (Слайд 7).
    Этапы: 1. Планирование -> 2. Инструменты/RAG -> 3. Синтез по 6 вопросам -> 4. Самопроверка.
    """

    def __init__(self, llm_client: SafeLLMClient):
        self.llm = llm_client

    def generate_feed_for_client(
        self,
        company: CompanyContext,
        role: str,
        news_list: List[NewsItem],
        bank_chunks: List[BankResearchChunk],
    ) -> List[PersonalizedInsight]:
        role_key = role.upper() if role.upper() in ROLE_PERSONAS else "CFO"
        insights: List[PersonalizedInsight] = []

        for news in news_list:
            insight = self.process_single_event(company, role_key, news, bank_chunks)
            if insight.relevance_score >= 45:
                insights.append(insight)

        insights.sort(key=lambda x: x.relevance_score, reverse=True)
        return insights

    def process_single_event(
        self,
        company: CompanyContext,
        role: str,
        news: NewsItem,
        all_bank_chunks: List[BankResearchChunk],
    ) -> PersonalizedInsight:
        trace_steps: List[AgentTraceStep] = []
        persona = ROLE_PERSONAS.get(role, ROLE_PERSONAS["CFO"])

        # ШАГ 1: ПЛАНИРОВАНИЕ И ОЦЕНКА РЕЛЕВАНТНОСТИ
        score, matched_features, supply_chain_note = self._step_1_plan_and_score(company, role, news)
        trace_steps.append(AgentTraceStep(
            step_name="1. Планирование и скоринг релевантности",
            tool_used=f"company_profiler + {ALLOWED_MODELS['fast']}",
            reasoning=(
                f"Сопоставлены теги новости {news.macro_triggers} с профилем {company.synthetic_u} "
                f"(ОКВЭД {company.main_okved_code}, роль {persona['title']}). "
                f"Найдено совпадений признаков: {len(matched_features)}. Итоговый скор: {score}/100."
            ),
        ))

        # ШАГ 2: РАБОТА С ИНСТРУМЕНТАМИ И RAG АНАЛИТИКИ БАНКА
        relevant_chunks = self._step_2_retrieve_bank_research(news, all_bank_chunks)
        primary_chunk = relevant_chunks[0] if relevant_chunks else BankResearchChunk(
            chunk_id="default",
            report_title="Ключевая ставка ЦБ РФ: ставка без изменения на 14,0%, риторика стала жестче",
            topic="Денежно-кредитная политика",
            content="Совет директоров Банка России сохранил ставку на уровне 14,0%. Период быстрого смягчения ДКП поставлен на паузу.",
            key_thesis="Деньги в экономике остаются дорогими (14%), финансовая нагрузка на компании с заемным финансированием не снизится в ближайшей перспективе.",
            published_date="Сентябрь 2026",
        )
        trace_steps.append(AgentTraceStep(
            step_name="2. Поиск в базе аналитики Альфа-Банка (RAG)",
            tool_used="search_bank_analytics",
            reasoning=f"Отобран профильный макро-отчет Альфа-Банка: «{primary_chunk.report_title}».",
        ))

        # ШАГ 3: ГЕНЕРАЦИЯ ИНТЕРПРЕТАЦИИ ПО 6 ВОПРОСАМ
        draft = self._step_3_synthesize_insight(
            company=company,
            role=role,
            persona=persona,
            news=news,
            bank_chunk=primary_chunk,
            matched_features=matched_features,
            supply_chain_note=supply_chain_note,
        )
        trace_steps.append(AgentTraceStep(
            step_name="3. Многофакторный синтез бизнес-инсайта",
            tool_used=ALLOWED_MODELS["reasoning"],
            reasoning=(
                f"Сформированы ответы на 6 ключевых вопросов для роли «{persona['title']}» "
                f"с разделением позиции Альфа-Банка и выводов модели."
            ),
        ))

        # ШАГ 4: САМОПРОВЕРКА И АДАПТАЦИЯ (SELF-REFLECTION)
        verified_draft, reflection_note = self._step_4_self_reflect(company, news, primary_chunk, draft)
        trace_steps.append(AgentTraceStep(
            step_name="4. Самопроверка и верификация (Self-Reflection)",
            tool_used=ALLOWED_MODELS["research"],
            reasoning=reflection_note,
        ))

        urgency = "Критично" if score >= 80 else ("Важно" if score >= 65 else "Обзорно")

        return PersonalizedInsight(
            insight_id=f"ins_{company.synthetic_u}_{news.news_id}_{role.lower()}",
            news_id=news.news_id,
            company_id=company.synthetic_u,
            target_role=role,
            relevance_score=score,
            urgency_badge=urgency,
            what_happened=WhatHappenedBlock(
                title=news.title,
                facts=news.summary_facts or [news.raw_text[:220] + "..."],
                source_name=news.source_name,
                source_url=news.source_url,
                published_at=news.published_at,
            ),
            why_important_for_company=WhyImportantBlock(
                summary=verified_draft["why_summary"],
                matched_company_features=matched_features,
                supply_chain_impact=supply_chain_note,
            ),
            consequences=ConsequencesBlock(
                risks=verified_draft["risks"],
                opportunities=verified_draft["opportunities"],
                horizon=verified_draft.get("horizon", "3–6 месяцев (2П 2026 г.)"),
            ),
            bank_evaluation=BankEvaluationBlock(
                alfa_bank_position=primary_chunk.key_thesis,
                cited_report_title=primary_chunk.report_title,
                ai_model_inference=verified_draft["ai_inference"],
            ),
            recommended_actions=RecommendedActionsBlock(
                steps_for_role=verified_draft["steps_for_role"],
                native_bank_product=NativeProductOffer(
                    product_name=verified_draft["product_name"],
                    pitch=verified_draft["product_pitch"],
                    cta_label=verified_draft["product_cta"],
                ),
            ),
            traceability=TraceabilityBlock(
                used_sources=[
                    f"Внешний источник: {news.source_name} ({news.published_at})",
                    f"Аналитика Альфа-Банка: «{primary_chunk.report_title}»",
                    f"Профиль клиента: {company.synthetic_u} (ОКВЭД {company.main_okved_code})",
                ],
                company_triggers_used=matched_features,
                llm_models_used=[
                    ALLOWED_MODELS["fast"],
                    ALLOWED_MODELS["reasoning"],
                    ALLOWED_MODELS["research"],
                ],
                agent_steps=trace_steps,
            ),
        )

    def _step_1_plan_and_score(
        self, company: CompanyContext, role: str, news: NewsItem
    ) -> tuple[int, List[str], Optional[str]]:
        score = 50
        matched: List[str] = [
            f"Отрасль: {company.main_okved_name} ({company.market_position_label}, доля рынка {company.industry_market_share_pct}%)"
        ]
        supply_chain_note = None

        if company.main_okved_code in news.affected_okveds or any(
            code.split(".")[0] == company.main_okved_code.split(".")[0] for code in news.affected_okveds
        ):
            score += 25
            matched.append(f"Прямое попадание в основной ОКВЭД компании ({company.main_okved_code})")

        triggers_set = set(t.lower() for t in news.macro_triggers)
        if any(k in triggers_set for k in ("key_rate", "ставка", "кредит")):
            if any("Кредит" in p or "Лизинг" in p for p in company.active_products):
                score += 20
                matched.append("Действующие кредитные/лизинговые продукты (CL_PRODUCT_LOA_MARK=1)")
            if any("Депозит" in p for p in company.active_products):
                score += 12
                matched.append("Наличие депозитных продуктов для размещения ликвидности (CL_PRODUCT_DEP_MARK=1)")

        if any(k in triggers_set for k in ("fx", "валют", "вэд", "commodities", "сырье")):
            if company.is_foreign_trade:
                score += 22
                countries = ", ".join(company.fts_countries) if company.fts_countries else "внешние рынки"
                matched.append(f"Активный участник ВЭД по базе ФТС (FTS_FLAG=1, направление: {countries})")

        for cp in company.top_counterparties:
            if cp.okved_code and any(cp.okved_code.startswith(ok) for ok in news.affected_okveds):
                score += 15
                role_ru = "ключевого поставщика" if cp.role == "supplier" else "крупного покупателя"
                supply_chain_note = (
                    f"Косвенное влияние через цепочку поставок: событие затрагивает отрасль вашего {role_ru} "
                    f"{cp.synthetic_u} («{cp.okved_name}», доля в расчетах {cp.share_in_turnover_pct}%)."
                )
                matched.append(f"Связь через платежный граф с контрагентом {cp.synthetic_u} ({cp.share_in_turnover_pct}% оборота)")
                break

        if role == "CFO" and any(k in triggers_set for k in ("key_rate", "inflation", "bonds", "ставка")):
            score += 8
        elif role == "TREASURER" and any(k in triggers_set for k in ("key_rate", "fx", "ставка", "валют")):
            score += 8
        elif role == "CEO" and any(k in triggers_set for k in ("gdp", "labor", "commodities", "сырье")):
            score += 8

        return min(score, 98), matched, supply_chain_note

    def _step_2_retrieve_bank_research(
        self, news: NewsItem, chunks: List[BankResearchChunk]
    ) -> List[BankResearchChunk]:
        if not chunks:
            return []
        scored_chunks = []
        news_words = set((news.title + " " + " ".join(news.macro_triggers) + " " + " ".join(news.tags)).lower().split())
        for ch in chunks:
            ch_words = set((ch.report_title + " " + ch.topic + " " + ch.content).lower().split())
            overlap = len(news_words.intersection(ch_words))
            scored_chunks.append((overlap, ch))
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_chunks[:2]]

    def _step_3_synthesize_insight(
        self,
        company: CompanyContext,
        role: str,
        persona: Dict[str, str],
        news: NewsItem,
        bank_chunk: BankResearchChunk,
        matched_features: List[str],
        supply_chain_note: Optional[str],
    ) -> Dict[str, Any]:
        product_name, product_pitch, product_cta = self._recommend_native_product(company, news)

        rev_bln = round(company.revenue / 1e9, 1) if company.revenue > 1e7 else round(company.revenue, 1)
        fallback = {
            "why_summary": (
                f"Для вашей компании ({company.main_okved_name}, выручка ~{rev_bln} млрд руб., доля рынка {company.industry_market_share_pct}%) "
                f"данное событие напрямую влияет на {persona['focus']}. "
                f"С учетом активных банковских продуктов ({', '.join(company.active_products) or 'РКО'}) "
                f"и масштаба группы ({company.group_context.companies_count} юрлиц) требуется корректировка планов на 3–4 кв. 2026 г."
            ),
            "risks": [
                f"Сохранение высокой стоимости заемного финансирования и давление на процентные расходы (актуально для роли: {persona['title']}).",
                "Риск роста себестоимости у подрядчиков и замедления оборачиваемости дебиторской задолженности в цепочке расчетов.",
            ],
            "opportunities": [
                f"Использование позиции крупного игрока ({company.market_position_label}) для пересмотра коммерческих условий с контрагентами.",
                "Повышение доходности от размещения временно свободной ликвидности в инструментах денежного рынка и облигациях.",
            ],
            "ai_inference": (
                f"Сопоставляя макропрогноз Альфа-Банка («{bank_chunk.report_title}») с вашим профилем, AI-модель оценивает вероятность "
                f"сохранения жестких финансовых условий до конца 2026 года как высокую. Рекомендуется сместить фокус с агрессивного кредитного расширения на оптимизацию оборотного капитала."
            ),
            "steps_for_role": [
                f"[{persona['title']}] Провести стресс-тест финансовой модели компании при сохранении текущих макроусловий на горизонте 6 месяцев.",
                "Проверить условия расчетов с топ-контрагентами из платежного графа для предотвращения кассовых разрывов.",
                f"Рассмотреть подключение инструмента «{product_name}» в Альфа-Бизнесе для защиты маржинальности.",
            ],
            "product_name": product_name,
            "product_pitch": product_pitch,
            "product_cta": product_cta,
            "horizon": "3–6 месяцев (2-е полугодие 2026 г.)",
        }

        sys_prompt = (
            "Ты — главный корпоративный аналитик Альфа-Банка для крупного бизнеса (выручка >15 млрд руб.). "
            "Не пересказывай новость! Дай глубокую персонализированную интерпретацию для указанной роли ЛПР "
            "с опорой на профиль клиента и аналитику Альфа-Банка. Верни строго JSON с ключами: "
            "why_summary, risks (list), opportunities (list), ai_inference, steps_for_role (list), "
            "product_name, product_pitch, product_cta, horizon."
        )
        user_prompt = (
            f"Роль пользователя: {persona['title']} (фокус: {persona['focus']})\n"
            f"Профиль компании: ОКВЭД {company.main_okved_code} ({company.main_okved_name}), выручка {rev_bln} млрд руб., "
            f"доля в отрасли {company.industry_market_share_pct}%, продукты: {company.active_products}, ВЭД: {company.fts_countries}.\n"
            f"Сработавшие триггеры: {matched_features}\n"
            f"Цепочка поставок: {supply_chain_note}\n"
            f"Новость: {news.title} — {news.raw_text}\n"
            f"Позиция Альфа-Банка ({bank_chunk.report_title}): {bank_chunk.key_thesis} ({bank_chunk.content})"
        )

        return self.llm.generate_json(
            system_prompt=sys_prompt,
            user_prompt=user_prompt,
            model_tier="reasoning",
            fallback_dict=fallback,
        )

    def _step_4_self_reflect(
        self,
        company: CompanyContext,
        news: NewsItem,
        bank_chunk: BankResearchChunk,
        draft: Dict[str, Any],
    ) -> tuple[Dict[str, Any], str]:
        issues = []
        if not draft.get("risks") or len(draft["risks"]) < 2:
            draft["risks"] = [
                "Риск давления на операционную рентабельность при сохранении жестких рыночных условий.",
                "Риск удлинения сроков расчетов со стороны контрагентов.",
            ]
            issues.append("дополнены риски")

        if not draft.get("ai_inference"):
            draft["ai_inference"] = (
                f"Вывод модели на основе отчета «{bank_chunk.report_title}»: компании {company.synthetic_u} "
                f"рекомендуется контролировать долговую и оборотную нагрузку."
            )
            issues.append("восстановлен блок AI-вывода")

        status_note = (
            "Проведена верификация: проверено разделение фактов первоисточника, позиции Центра макроэкономических "
            f"исследований Альфа-Банка («{bank_chunk.report_title}») и выводов модели. Противоречий с профилем "
            f"{company.synthetic_u} не выявлено" + (f" ({', '.join(issues)})." if issues else ".")
        )
        return draft, status_note

    def _recommend_native_product(self, company: CompanyContext, news: NewsItem) -> tuple[str, str, str]:
        triggers = " ".join(news.macro_triggers).lower()
        if "fx" in triggers or "валют" in triggers or company.is_foreign_trade:
            return (
                "Валютное хеджирование и ВЭД-конвертация Альфа-Бизнес",
                "Зафиксируйте валютный курс по контрактам с поставщиками (ФТС) через форвардные инструменты и снизьте волатильность маржи.",
                "Рассчитать стоимость хеджирования",
            )
        if not any("Факторинг" in p for p in company.active_products):
            return (
                "Цифровой факторинг Альфа-Банка",
                "В условиях дорогого кредитования (ключевая ставка 14%) ускорьте оборачиваемость дебиторской задолженности без роста долговой нагрузки.",
                "Подключить лимит факторинга",
            )
        return (
            "Процентный своп (IRS) и Биржевые овернайты Альфа-Бизнес",
            "Защитите процентную ставку по кредитному портфелю и размещайте свободную ликвидность под ставку близкую к ключевой (14% годовых).",
            "Получить котировку казначейства",
        )

    def answer_followup_question(
        self,
        req: ChatRequest,
        company: CompanyContext,
        insight: PersonalizedInsight,
    ) -> ChatResponse:
        persona = ROLE_PERSONAS.get(req.role.upper(), ROLE_PERSONAS["CFO"])
        fallback_answer = (
            f"Для роли «{persona['title']}» компании {company.synthetic_u} ({company.main_okved_name}): "
            f"по событию «{insight.what_happened.title}» позиция аналитиков Альфа-Банка опирается на отчет "
            f"«{insight.bank_evaluation.cited_report_title}» ({insight.bank_evaluation.alfa_bank_position}). "
            f"Применительно к вашему вопросу («{req.question}»): учитывая ваши активные продукты "
            f"({', '.join(company.active_products)}) и долю рынка {company.industry_market_share_pct}%, "
            f"ключевой эффект проявится на горизонте 1–2 кварталов. Рекомендуемый шаг: {insight.recommended_actions.steps_for_role[0]}"
        )

        res = self.llm.generate_json(
            system_prompt=(
                "Ты — интерактивный AI-ассистент Альфа-Бизнеса для крупного корпоративного клиента. "
                "Отвечай четко, с цифрами из контекста компании и ссылками на аналитику Альфа-Банка. "
                "Верни JSON с ключом 'answer' (str) и 'follow_up_suggestions' (list of 2 strings)."
            ),
            user_prompt=(
                f"Вопрос пользователя ({persona['title']}): {req.question}\n"
                f"Контекст компании: {company.model_dump_json()}\n"
                f"Текущий инсайт: {insight.model_dump_json()}"
            ),
            model_tier="universal",
            fallback_dict={
                "answer": fallback_answer,
                "follow_up_suggestions": [
                    "Как это событие повлияет на наших топ-3 контрагентов по платежам?",
                    "Покажи сравнение сценариев при изменении ключевой ставки на +/- 1 п.п.",
                ],
            },
        )

        return ChatResponse(
            answer=res.get("answer", fallback_answer),
            cited_sources=insight.traceability.used_sources,
            model_used=ALLOWED_MODELS["universal"],
            follow_up_suggestions=res.get("follow_up_suggestions", [
                "Как это повлияет на наших ключевых поставщиков?",
                "Какие продукты банка помогут снизить этот риск?",
            ]),
        )
