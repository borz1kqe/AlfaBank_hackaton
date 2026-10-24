# src/services/llm_client.py
import os
import re
import json
import sqlite3
import hashlib
from typing import Optional, Dict, Any, List
from openai import OpenAI, APITimeoutError, APIConnectionError
from dotenv import load_dotenv

load_dotenv()

# Строгий белый список моделей из Приложения 3 (Слайд 18)
ALLOWED_MODELS = {
    "fast": "Gemma 4 26B A4B",           # Классификация, скоринг, извлечение фактов
    "reasoning": "GLM-5.3-Flash",        # Глубокий анализ и рассуждения
    "universal": "Qwen3.6 35B A3B",      # Генерация и обработка материалов
    "research": "DeepSeek-V4.1-Flash",   # Поиск взаимосвязей и самопроверка
    "vision": "Qwen3-VL-30B-A3B-Instruct",
    "text": "Kimi-K2.6",
}

# Идентификаторы моделей на шлюзе (отличаются от «человеческих» названий выше).
# Можно переопределить через переменные окружения LLM_MODEL_REASONING и т.д.
GATEWAY_SLUGS = {
    "reasoning": os.getenv("LLM_MODEL_REASONING", "z-ai/glm-5.3-flash"),
    "universal": os.getenv("LLM_MODEL_UNIVERSAL", "qwen/qwen3.6-35b-a3b"),
    "research": os.getenv("LLM_MODEL_RESEARCH", "deepseek/deepseek-v4.1-flash"),
}
DEFAULT_GATEWAY_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-v4.1-flash")


def _parse_json_loose(text: str) -> Dict[str, Any]:
    """Достаёт JSON даже если модель обернула его в ```json ... ```."""
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise


class SafeLLMClient:
    """
    Безопасный клиент для работы с разрешенными LLM (Ограничения 04 и 06).
    Включает SQLite-кэширование для защиты дневного лимита 500 руб.
    """

    def __init__(self, cache_db_path: str = "data/llm_cache.sqlite"):
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.cache_db_path = cache_db_path
        os.makedirs(os.path.dirname(self.cache_db_path), exist_ok=True)
        self._init_cache_db()

        # Счётчики режимов работы: live — ответ от модели, cached — из кэша, fallback — детерминированный синтез
        self.stats: Dict[str, int] = {"live": 0, "cached": 0, "fallback": 0}
        self.last_error: str = ""
        self.last_model: str = ""

        self.client: Optional[OpenAI] = None
        if self.api_key and self.api_key != "your_key_here":
            # Короткий таймаут и без повторов: демо не должно зависать на 10 минут
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=float(os.getenv("LLM_TIMEOUT", "45")),
                max_retries=0,
            )

    def _init_cache_db(self):
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS llm_cache (
                    prompt_hash TEXT PRIMARY KEY,
                    model TEXT,
                    response_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _get_cached(self, prompt_hash: str) -> Optional[str]:
        with sqlite3.connect(self.cache_db_path) as conn:
            row = conn.execute(
                "SELECT response_text FROM llm_cache WHERE prompt_hash = ?",
                (prompt_hash,)
            ).fetchone()
            return row[0] if row else None

    def _save_cache(self, prompt_hash: str, model: str, response_text: str):
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO llm_cache (prompt_hash, model, response_text) VALUES (?, ?, ?)",
                (prompt_hash, model, response_text)
            )

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        model_tier: str = "reasoning",
        fallback_dict: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        model_name = ALLOWED_MODELS.get(model_tier, ALLOWED_MODELS["universal"])
        if model_name not in ALLOWED_MODELS.values():
            raise PermissionError(f"Модель {model_name} не входит в список разрешенных (Приложение 3).")

        raw_key = f"{model_name}||{system_prompt}||{user_prompt}"
        prompt_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

        cached = self._get_cached(prompt_hash)
        if cached:
            try:
                data = json.loads(cached)
                self.stats["cached"] += 1
                return data
            except json.JSONDecodeError:
                pass

        if self.client is not None:
            candidates: List[str] = []
            # сначала проверенная модель шлюза; модель «по регламенту» — второй попыткой.
            # LLM_PREFER_TIER_MODELS=1 меняет порядок.
            order = (GATEWAY_SLUGS.get(model_tier), DEFAULT_GATEWAY_MODEL)
            if os.getenv("LLM_PREFER_TIER_MODELS") != "1":
                order = order[::-1]
            for m in order:
                if m and m not in candidates:
                    candidates.append(m)

            network_down = False
            for gw_model in candidates:
                if network_down:
                    break
                for use_json_mode in (True, False):
                    try:
                        kwargs: Dict[str, Any] = dict(
                            model=gw_model,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt},
                            ],
                            temperature=0.2,
                        )
                        if use_json_mode:
                            kwargs["response_format"] = {"type": "json_object"}
                        resp = self.client.chat.completions.create(**kwargs)
                        content = resp.choices[0].message.content or "{}"
                        data = _parse_json_loose(content)
                        self._save_cache(prompt_hash, model_name, json.dumps(data, ensure_ascii=False))
                        self.stats["live"] += 1
                        self.last_model = gw_model
                        return data
                    except (APITimeoutError, APIConnectionError) as e:
                        print(f"[LLM Warning] Шлюз недоступен ({e}), переключаемся на детерминированный синтез.")
                        self.last_error = f"{gw_model}: {type(e).__name__}"
                        network_down = True
                        break
                    except Exception as e:
                        print(f"[LLM Warning] {gw_model} (json_mode={use_json_mode}): {e}")
                        self.last_error = f"{gw_model}: {str(e)[:160]}"
                        msg = str(e).lower()
                        if use_json_mode and ("response_format" in msg or "json" in msg):
                            continue  # шлюз не поддерживает JSON-режим — пробуем без него
                        break  # модель недоступна — пробуем следующую

        self.stats["fallback"] += 1
        if self.client is None:
            self.last_error = "ключ LLM_API_KEY не задан — клиент не создан"
        return fallback_dict or {}
