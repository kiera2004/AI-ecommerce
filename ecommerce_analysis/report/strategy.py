"""运营策略生成"""
from __future__ import annotations

from typing import Any

from utils.i18n import LANG_ZH, t
from utils.llm_client import call_deepseek, load_prompt


def generate_strategy(
    root_cause_result: dict[str, Any],
    metrics_summary: str = "",
    lang: str = LANG_ZH,
) -> str:
    prompt_tpl = load_prompt("strategy_prompt.txt", lang)
    data = {
        "metrics_summary": metrics_summary,
        "attribution": root_cause_result.get("attribution_chains", []),
        "llm_root_cause": root_cause_result.get("llm_analysis", ""),
        "drill_down_keys": list(root_cause_result.get("drill_down", {}).keys()),
    }
    system = prompt_tpl.format(data=str(data))
    return call_deepseek(system, t("llm.strategy_user", lang), lang=lang)


if __name__ == "__main__":
    demo = {"attribution_chains": ["test"], "llm_analysis": "", "drill_down": {}}
    try:
        print(generate_strategy(demo)[:200])
    except Exception as e:
        print("Skip LLM:", e)
