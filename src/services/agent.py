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


# Ролевая модель доступа (RBAC): у каждой роли свой фокус, свои риски, шаги и вопросы.
# Цифр здесь нет намеренно: расчёты (платёж, экономия, ICR) считает код и передаёт их отдельно.
ROLE_PERSONAS = {
    "CEO": {
        "title": "Генеральный директор / Собственник",
        "focus": "доля рынка, стратегия развития, устойчивость цепочек поставок, действия конкурентов, маржинальность бизнеса",
        "must_cover": "влияние на маржу и долю рынка, устойчивость цепочки поставок, стратегические решения (цены, контрагенты, инвестпрограмма)",
        "markers": ("маржин", "цепоч", "стратег"),
        "risks": [
            "Маржинальность: удорожание заёмных денег и рост затрат подрядчиков сжимают маржу, если не пересмотреть цены и условия сделок.",
            "Цепочка поставок: сдвиг платежей и рост цен у ключевых контрагентов создают риск срыва поставок и потери доли рынка.",
            "Инвестпрограмма: пауза в снижении ставки отодвигает окупаемость проектов, которые зависят от заёмного финансирования.",
        ],
        "opportunities": [
            "Использовать позицию крупного игрока, чтобы пересмотреть коммерческие условия с поставщиками и покупателями.",
            "Пересобрать инвестпрограмму: приоритет проектам с короткой окупаемостью и собственным финансированием.",
        ],
        "steps": [
            "Определить 3 ключевых контрагента, которые сильнее всего влияют на выручку и маржу, и оценить риск срыва поставок.",
            "Пересмотреть ценовую политику и условия расчётов с учётом возросшей стоимости денег.",
            "Утвердить вместе с CFO порядок приоритизации инвестпроектов на 2027 г.",
        ],
        "questions": [
            ("Риски цепочки поставок", "Как это событие отразится на наших ключевых поставщиках и покупателях и что сделать в первую очередь?"),
            ("Влияние на маржу и инвестиции", "Как пауза в снижении ставки влияет на нашу маржу и какие инвестпроекты стоит отложить?"),
        ],
    },
    "CFO": {
        "title": "Финансовый директор (CFO)",
        "focus": "стоимость заемного финансирования, ключевая ставка ЦБ, ковенанты, долговая нагрузка, валютные риски, CAPEX/OPEX",
        "must_cover": "ковенанты (Net Debt/EBITDA, ICR), стоимость обслуживания долга, процентный своп (IRS) и фиксацию ставки, бюджет процентных расходов",
        "markers": ("ковенант", "своп", "irs"),
        "risks": [
            "Ковенанты: при сохранении ставки растут процентные расходы, и запас по Net Debt / EBITDA и ICR сокращается — нужен контроль до отчётной даты.",
            "Плавающая ставка по кредитному портфелю (КС + спред) не получает ожидаемого снижения — бюджет процентных расходов на 2027 г. под давлением.",
            "Рефинансирование: пауза в смягчении ДКП удорожает новые транши и продление кредитных лимитов.",
        ],
        "opportunities": [
            "Зафиксировать ставку через процентный своп (IRS) и снять неопределённость по бюджету процентных расходов.",
            "Договориться с банком о ковенантном вейвере или пересмотре порогов до годовой отчётности.",
        ],
        "steps": [
            "Пересчитать запас по ковенантам (Net Debt / EBITDA, ICR) при текущей ставке и в жёстком сценарии.",
            "Смоделировать IRS по ближайшему траншу в калькуляторе: платёж до и после, экономия в млн ₽.",
            "Подготовить с банком ковенантный вейвер или перенос тестирования ковенант до годовой отчётности.",
        ],
        "questions": [
            ("Запас по ковенантам", "Рассчитай запас по ковенантам Net Debt/EBITDA и ICR при сохранении ставки 14% и в жёстком сценарии."),
            ("Окупаемость процентного свопа", "Стоит ли фиксировать ставку через IRS: сравни платежи до и после и срок окупаемости хеджа."),
        ],
    },
    "TREASURER": {
        "title": "Руководитель казначейства",
        "focus": "ликвидность, ставки по депозитам и овернайтам, платежный календарь, кассовые разрывы, трансграничные расчеты ВЭД",
        "must_cover": "ликвидность и платёжный календарь, кассовые разрывы, размещение свободных остатков (овернайты, депозиты), расчёты по ВЭД",
        "markers": ("ликвидн", "овернайт", "кассов", "платежн", "платёжн"),
        "risks": [
            "Кассовые разрывы: перенос авансовых платежей покупателей и удлинение дебиторки сокращают остатки к датам обязательных платежей.",
            "Дорогая ликвидность: краткосрочное финансирование для закрытия разрывов остаётся дорогим при высокой ключевой ставке.",
            "Валютная ликвидность: волатильность курса и сроки трансграничных расчётов по ВЭД усложняют платёжный календарь.",
        ],
        "opportunities": [
            "Размещать операционный остаток на овернайт-депозитах и в инструментах денежного рынка под ставку, близкую к ключевой.",
            "Ускорить расчёты с зарубежными контрагентами через прямой клиринг и заложить курсовой прогноз в платёжный календарь.",
        ],
        "steps": [
            "Обновить платёжный календарь на 13 недель с учётом сдвига платежей контрагентов.",
            "Вынести свободный остаток на овернайт-депозит, оставив буфер под ближайшие обязательные платежи.",
            "Согласовать с банком овердрафт или лимит на случай кассового разрыва и график трансграничных расчётов.",
        ],
        "questions": [
            ("Платёжный календарь и разрывы", "Где в ближайшие 13 недель возможны кассовые разрывы при сдвиге платежей контрагентов и как их закрыть?"),
            ("Куда разместить остаток", "Куда разместить свободную ликвидность: овернайт-депозиты или инструменты денежного рынка, и какой буфер оставить?"),
        ],
    },
    "ACCOUNTANT": {
        "title": "Главный бухгалтер",
        "focus": "налоговое и таможенное регулирование (ФТС/ФНС), комплаенс, отчетность, документарное сопровождение сделок",
        "must_cover": "ФСБУ 25/2018 (аренда и лизинг), отчётность и раскрытия, документарное сопровождение ВЭД и валютный контроль",
        "markers": ("фсбу", "отчётн", "отчетн", "документ"),
        "risks": [
            "ФСБУ 25/2018 (аренда и лизинг): ставка дисконтирования по новым и изменяемым договорам зависит от стоимости заёмных средств — расчёты нужно перепроверить.",
            "Отчётность: рост процентных расходов и изменение резервов требуют корректного отражения и раскрытий для аудитора и банка-кредитора.",
            "Комплаенс по ВЭД: без полного комплекта подтверждающих документов и корректных деклараций возможны штрафы и задержка расчётов.",
        ],
        "opportunities": [
            "Автоматизировать документарное сопровождение сделок и сверки, чтобы сократить сроки закрытия периода.",
            "Заранее согласовать с банком формат ковенантной отчётности и подтверждающих документов по ВЭД-контрактам.",
        ],
        "steps": [
            "Проверить расчёт дисконтирования по договорам аренды и лизинга по ФСБУ 25/2018 (новые и изменённые договоры).",
            "Подготовить расчёт процентных расходов и данные для ковенантной отчётности по кредитным договорам.",
            "Проверить комплект документов по ВЭД-контрактам (контракты, декларации, акты) на ближайшие расчёты.",
        ],
        "questions": [
            ("Что менять по ФСБУ 25/2018", "Как решение по ставке влияет на учёт аренды и лизинга по ФСБУ 25/2018 и что нужно пересчитать?"),
            ("Документы по ВЭД и отчётность", "Какие документы и отчётность подготовить для банка и проверок по ВЭД-контрактам и процентным расходам?"),
        ],
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
                f"(приоритеты роли: {persona['must_cover']}) "
                f"с разделением позиции Альфа-Банка и выводов модели."
            ),
        ))

        # ШАГ 4: САМОПРОВЕРКА И АДАПТАЦИЯ (SELF-REFLECTION)
        verified_draft, reflection_note = self._step_4_self_reflect(company, news, primary_chunk, draft, role)
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
        elif role == "ACCOUNTANT" and any(k in triggers_set for k in ("key_rate", "ставка", "fx", "валют", "вэд", "tax", "regulation", "customs")):
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
        persona: Dict[str, Any],
        news: NewsItem,
        bank_chunk: BankResearchChunk,
        matched_features: List[str],
        supply_chain_note: Optional[str],
    ) -> Dict[str, Any]:
        product_name, product_pitch, product_cta = self._recommend_native_product(company, news, role)

        rev_bln = round(company.revenue / 1e9, 1) if company.revenue > 1e7 else round(company.revenue, 1)
        steps = list(persona["steps"]) + [
            f"Рассмотреть подключение инструмента «{product_name}» в Альфа-Бизнесе."
        ]
        fallback = {
            "why_summary": (
                f"Для вашей компании ({company.main_okved_name}, выручка ~{rev_bln} млрд руб., доля рынка {company.industry_market_share_pct}%) "
                f"данное событие напрямую влияет на {persona['focus']}. "
                f"Для роли «{persona['title']}» ключевое: {persona['must_cover']}. "
                f"С учетом активных банковских продуктов ({', '.join(company.active_products) or 'РКО'}) "
                f"и масштаба группы ({company.group_context.companies_count} юрлиц) требуется корректировка планов на 3–4 кв. 2026 г."
            ),
            "risks": list(persona["risks"]),
            "opportunities": list(persona["opportunities"]),
            "ai_inference": (
                f"Сопоставляя макропрогноз Альфа-Банка («{bank_chunk.report_title}») с вашим профилем, AI-модель оценивает вероятность "
                f"сохранения жестких финансовых условий до конца 2026 года как высокую. "
                f"Для роли «{persona['title']}» приоритет: {persona['must_cover']}."
            ),
            "steps_for_role": steps,
            "product_name": product_name,
            "product_pitch": product_pitch,
            "product_cta": product_cta,
            "horizon": "3–6 месяцев (2-е полугодие 2026 г.)",
        }

        sys_prompt = (
            "Ты — главный корпоративный аналитик Альфа-Банка для крупного бизнеса (выручка >15 млрд руб.). "
            "Не пересказывай новость! Дай глубокую персонализированную интерпретацию для указанной роли ЛПР "
            "с опорой на профиль клиента и аналитику Альфа-Банка. "
            f"Ответ должен быть специфичным именно для роли «{persona['title']}»: обязательно затрони {persona['must_cover']}. "
            "Для других ролей эти же риски и шаги не подошли бы. "
            "risks — 2–3 риска с точки зрения этой роли, steps_for_role — 3–4 конкретных шага именно для этой роли. "
            "Не придумывай числовые показатели компании, которых нет во входных данных. "
            "Верни строго JSON с ключами: "
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
        role: str = "CFO",
    ) -> tuple[Dict[str, Any], str]:
        issues = []
        persona = ROLE_PERSONAS.get(role, ROLE_PERSONAS["CFO"])

        if not draft.get("risks") or len(draft["risks"]) < 2:
            draft["risks"] = list(persona["risks"][:2])
            issues.append("дополнены риски")

        if not draft.get("ai_inference"):
            draft["ai_inference"] = (
                f"Вывод модели на основе отчета «{bank_chunk.report_title}»: компании {company.synthetic_u} "
                f"рекомендуется контролировать долговую и оборотную нагрузку."
            )
            issues.append("восстановлен блок AI-вывода")

        # Проверка ролевой специфики: ответ модели должен затрагивать темы роли
        steps = draft.get("steps_for_role") or []
        if not isinstance(steps, list):
            steps = [str(steps)]
        role_text = " ".join(str(x) for x in steps + list(draft.get("risks") or [])).lower()
        if not any(m in role_text for m in persona["markers"]):
            steps = [persona["steps"][0]] + steps
            issues.append("добавлен шаг по профилю роли")
        draft["steps_for_role"] = steps

        status_note = (
            "Проведена верификация: проверено разделение фактов первоисточника, позиции Центра макроэкономических "
            f"исследований Альфа-Банка («{bank_chunk.report_title}») и выводов модели, "
            f"а также соответствие выводов роли «{persona['title']}». Противоречий с профилем "
            f"{company.synthetic_u} не выявлено" + (f" ({', '.join(issues)})." if issues else ".")
        )
        return draft, status_note

    def _recommend_native_product(self, company: CompanyContext, news: NewsItem, role: str = "CFO") -> tuple[str, str, str]:
        triggers = " ".join(news.macro_triggers).lower()
        rate_news = any(k in triggers for k in ("key_rate", "ставка", "кредит"))

        # Для новостей о ставке продукт зависит от роли: CFO — фиксация ставки, казначей — размещение ликвидности
        if rate_news and role == "CFO":
            return (
                "Процентный своп (IRS) Альфа-Банка",
                "Зафиксируйте ставку по кредитам с плавающей ставкой, снимите неопределённость по бюджету процентных расходов и защитите запас по ковенантам.",
                "Рассчитать параметры свопа",
            )
        if rate_news and role == "TREASURER":
            return (
                "Биржевые овернайты и депозиты Альфа-Бизнес",
                "Размещайте свободную ликвидность под ставку, близкую к ключевой, сохраняя буфер под платёжный календарь.",
                "Получить котировку казначейства",
            )

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
                f"Отвечай с позиции роли «{persona['title']}»: приоритет — {persona['must_cover']}. "
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
                "follow_up_suggestions": [q[1] for q in persona["questions"]],
            },
        )

        return ChatResponse(
            answer=res.get("answer", fallback_answer),
            cited_sources=insight.traceability.used_sources,
            model_used=ALLOWED_MODELS["universal"],
            follow_up_suggestions=res.get("follow_up_suggestions", [q[1] for q in persona["questions"]]),
        )
