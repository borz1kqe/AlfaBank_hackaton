# src/services/llm_client.py
import os
import re
import json
import time
import sqlite3
import hashlib
import threading
from collections import Counter
from typing import Optional, Dict, Any, List, Tuple
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
GATEWAY_SLUGS = {
    "reasoning": os.getenv("LLM_MODEL_REASONING", "z-ai/glm-5.3-flash"),
    "universal": os.getenv("LLM_MODEL_UNIVERSAL", "qwen/qwen3.6-35b-a3b"),
    "research": os.getenv("LLM_MODEL_RESEARCH", "deepseek/deepseek-v4.1-flash"),
}
DEFAULT_GATEWAY_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-v4.1-flash")
DEFAULT_BACKUP_URL = "https://api.alfahack-gateway26.ru/v1"

# Коды, при которых повторять запрос с тем же ключом бессмысленно
AUTH_CODES = {401, 402, 403}
# Коды, при которых имеет смысл один раз повторить после паузы
RETRY_CODES = {429, 500, 502, 503, 504}


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


def _status_code(e: Exception) -> Optional[int]:
    code = getattr(e, "status_code", None)
    if isinstance(code, int):
        return code
    resp = getattr(e, "response", None)
    code = getattr(resp, "status_code", None)
    return code if isinstance(code, int) else None


class SafeLLMClient:
    """
    Безопасный клиент для работы с разрешенными LLM (Ограничения 04 и 06).
    SQLite-кэш защищает дневной лимит, основной и резервный шлюзы дают отказоустойчивость,
    счётчики и last_error показывают реальное состояние в панели «Диагностика ИИ».
    """

    def __init__(self, cache_db_path: str = "data/llm_cache.sqlite"):
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.backup_url = os.getenv("LLM_BACKUP_URL", DEFAULT_BACKUP_URL).rstrip("/")
        self.cache_db_path = cache_db_path
        cache_dir = os.path.dirname(self.cache_db_path)
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
        self._init_cache_db()

        # Счётчики: live — ответ модели, cached — из кэша, fallback — детерминированный синтез
        self.stats: Dict[str, int] = {"live": 0, "cached": 0, "fallback": 0}
        self.models_used: Counter = Counter()      # какие модели реально ответили
        self.last_error: str = ""
        self.last_model: str = ""
        self.last_gateway: str = ""
        self._lock = threading.Lock()
        # Лимит параллельных запросов: лента шлёт события пачкой, шлюз такого не любит (429)
        self._sem = threading.Semaphore(int(os.getenv("LLM_MAX_CONCURRENCY", "3")))

        self.client: Optional[OpenAI] = None
        self._clients: List[Tuple[str, OpenAI]] = []
        if self.api_key and self.api_key != "your_key_here":
            timeout = float(os.getenv("LLM_TIMEOUT", "45"))
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url,
                                 timeout=timeout, max_retries=0)
            self._clients.append(("основной", self.client))
            if self.backup_url and self.backup_url != self.base_url:
                self._clients.append((
                    "резервный",
                    OpenAI(api_key=self.api_key, base_url=self.backup_url,
                           timeout=timeout, max_retries=0),
                ))

    # ---------- кэш ----------
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
        with sqlite3.connect(self.cache_db_path, timeout=10) as conn:
            row = conn.execute(
                "SELECT response_text FROM llm_cache WHERE prompt_hash = ?",
                (prompt_hash,),
            ).fetchone()
            return row[0] if row else None

    def _save_cache(self, prompt_hash: str, model: str, response_text: str):
        with sqlite3.connect(self.cache_db_path, timeout=10) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO llm_cache (prompt_hash, model, response_text) VALUES (?, ?, ?)",
                (prompt_hash, model, response_text),
            )

    # ---------- служебное ----------
    def _bump(self, key: str):
        with self._lock:
            self.stats[key] += 1

    def _set_error(self, msg: str):
        with self._lock:
            self.last_error = msg

    def _request(self, client: OpenAI, model: str, system_prompt: str,
                 user_prompt: str, json_mode: bool) -> str:
        """Один запрос; при 429/5xx один раз повторяет после паузы."""
        kwargs: Dict[str, Any] = dict(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        for attempt in (0, 1):
            try:
                with self._sem:
                    resp = client.chat.completions.create(**kwargs)
                return resp.choices[0].message.content or "{}"
            except (APITimeoutError, APIConnectionError):
                raise
            except Exception as e:
                if attempt == 0 and _status_code(e) in RETRY_CODES:
                    time.sleep(1.5)
                    continue
                raise
        return "{}"

    def ping(self) -> Dict[str, Any]:
        """Прямая проверка шлюза без кэша и без fallback. Для кнопки в диагностике."""
        if not self._clients:
            return {"ok": False, "error": "ключ LLM_API_KEY не задан — клиент не создан"}
        out: Dict[str, Any] = {"ok": False}
        for name, cl in self._clients:
            t0 = time.time()
            try:
                self._request(cl, DEFAULT_GATEWAY_MODEL, "Ответь одним словом.", "ping", False)
                out.update(ok=True, gateway=name, model=DEFAULT_GATEWAY_MODEL,
                           ms=int((time.time() - t0) * 1000))
                return out
            except Exception as e:
                out[f"ошибка ({name})"] = f"{type(e).__name__} [{_status_code(e)}]: {str(e)[:160]}"
        return out

    # ---------- основной вызов ----------
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
                self._bump("cached")
                return data
            except json.JSONDecodeError:
                pass

        if not self._clients:
            self._set_error("ключ LLM_API_KEY не задан — клиент не создан")
            self._bump("fallback")
            return fallback_dict or {}

        # сначала проверенная модель шлюза; модель «по регламенту» — второй попыткой.
        # LLM_PREFER_TIER_MODELS=1 меняет порядок.
        order = (GATEWAY_SLUGS.get(model_tier), DEFAULT_GATEWAY_MODEL)
        if os.getenv("LLM_PREFER_TIER_MODELS") != "1":
            order = order[::-1]
        candidates: List[str] = []
        for m in order:
            if m and m not in candidates:
                candidates.append(m)

        for gw_name, client in self._clients:
            skip_gateway = False
            for gw_model in candidates:
                if skip_gateway:
                    break
                for use_json_mode in (True, False):
                    try:
                        content = self._request(client, gw_model, system_prompt, user_prompt, use_json_mode)
                        data = _parse_json_loose(content)
                        self._save_cache(prompt_hash, model_name, json.dumps(data, ensure_ascii=False))
                        with self._lock:
                            self.stats["live"] += 1
                            self.last_model = gw_model
                            self.last_gateway = gw_name
                            self.models_used[gw_model] += 1
                        return data
                    except (APITimeoutError, APIConnectionError) as e:
                        print(f"[LLM Warning] {gw_name} шлюз недоступен ({e})")
                        self._set_error(f"{gw_name} шлюз: {type(e).__name__} (модель {gw_model})")
                        skip_gateway = True   # сеть лежит — пробуем резервный шлюз
                        break
                    except Exception as e:
                        code = _status_code(e)
                        print(f"[LLM Warning] {gw_name}/{gw_model} (json={use_json_mode}) [{code}]: {e}")
                        self._set_error(f"{gw_name}/{gw_model} [{code}]: {str(e)[:160]}")
                        if code in AUTH_CODES:
                            skip_gateway = True   # ключ/лимит — другая модель не поможет
                            break
                        msg = str(e).lower()
                        if use_json_mode and ("response_format" in msg or "json" in msg):
                            continue  # шлюз не поддерживает JSON-режим — пробуем без него
                        break  # модель недоступна — пробуем следующую

        self._bump("fallback")
        return fallback_dict or {}
