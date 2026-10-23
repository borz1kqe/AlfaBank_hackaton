# src/services/llm_client.py
import os
import json
import sqlite3
import hashlib
from typing import Optional, Dict, Any
from openai import OpenAI
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

        self.client: Optional[OpenAI] = None
        if self.api_key and self.api_key != "your_key_here":
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

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
                return json.loads(cached)
            except json.JSONDecodeError:
                pass

        if self.client is not None:
            try:
                resp = self.client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
                content = resp.choices[0].message.content or "{}"
                self._save_cache(prompt_hash, model_name, content)
                return json.loads(content)
            except Exception as e:
                print(f"[LLM Warning] Ошибка вызова API ({e}), переключаемся на детерминированный синтез.")

        return fallback_dict or {}
