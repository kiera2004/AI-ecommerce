"""DeepSeek API 封装（OpenAI 兼容）"""
from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from config import LLM_BASE_URL, LLM_MAX_RETRIES, LLM_MODEL, LLM_TEMPERATURE, PROMPTS_DIR
from utils.i18n import LANG_EN, LANG_ZH, t

load_dotenv()


def load_prompt(filename: str, lang: str = LANG_ZH) -> str:
    if lang == LANG_EN:
        en_name = filename.replace(".txt", "_en.txt")
        en_path = os.path.join(PROMPTS_DIR, en_name)
        if os.path.isfile(en_path):
            filename = en_name
    path = os.path.join(PROMPTS_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return f.read()


def call_deepseek(
    system_prompt: str,
    user_message: str,
    temperature: float | None = None,
    lang: str = LANG_ZH,
) -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        raise RuntimeError(t("llm.no_api_key", lang))

    client = OpenAI(api_key=api_key, base_url=LLM_BASE_URL.rstrip("/"))
    temp = LLM_TEMPERATURE if temperature is None else temperature
    last_err: Exception | None = None

    for attempt in range(1, LLM_MAX_RETRIES + 1):
        try:
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temp,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            last_err = e
            if attempt < LLM_MAX_RETRIES:
                time.sleep(1.5 * attempt)
    raise RuntimeError(t("llm.call_failed", lang, err=last_err))


if __name__ == "__main__":
    print("Prompt preview:", load_prompt("strategy_prompt.txt")[:80])
