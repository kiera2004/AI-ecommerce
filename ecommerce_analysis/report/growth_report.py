"""增长报告生成"""
from __future__ import annotations

from typing import Any

from utils.i18n import LANG_ZH, get_lang, t
from utils.llm_client import call_deepseek, load_prompt


def build_report_context(
    metrics: dict[str, Any],
    anomaly: dict[str, Any],
    root_cause: dict[str, Any],
    strategy: str,
) -> dict[str, Any]:
    return {
        "metrics_keys": list(metrics.keys()),
        "week_anomalies": anomaly.get("week_anomalies", []),
        "month_anomalies": anomaly.get("month_anomalies", []),
        "trends": anomaly.get("trend_texts", []),
        "attribution": root_cause.get("attribution_chains", []),
        "root_cause_llm": root_cause.get("llm_analysis", ""),
        "strategy": strategy,
        "cac_assumption": metrics.get("channel", {}).get("cac_assumption", ""),
    }


def generate_growth_report(context: dict[str, Any], lang: str | None = None) -> str:
    lang = lang or get_lang()
    prompt_tpl = load_prompt("report_prompt.txt", lang)
    system = prompt_tpl.format(data=str(context))
    return call_deepseek(system, t("llm.report_user", lang), lang=lang)


def report_to_markdown(report_text: str, lang: str | None = None) -> str:
    lang = lang or get_lang()
    title = t("report.title_md", lang)
    return f"# {title}\n\n{report_text}\n"


def export_markdown_bytes(md: str) -> bytes:
    return md.encode("utf-8")


def export_simple_pdf_bytes(md: str, title: str = "Growth Report") -> bytes:
    """简易 PDF：使用纯文本行写入（无额外依赖）。"""
    try:
        from io import BytesIO

        lines = [title, ""] + md.split("\n")
        content = "BT /F1 10 Tf 50 750 Td "
        for i, line in enumerate(lines[:60]):
            safe = line.replace("(", "\\(").replace(")", "\\)").replace("\\", "\\\\")[:80]
            if i == 0:
                content += f"({safe}) Tj "
            else:
                content += f"0 -14 Td ({safe}) Tj "
        content += "ET"
        stream = content.encode("latin-1", errors="replace")
        pdf = (
            b"%PDF-1.4\n1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
            b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n"
            b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources<< /Font<< /F1 5 0 R >> >> >>endobj\n"
            b"4 0 obj<< /Length " + str(len(stream)).encode() + b" >>stream\n" + stream + b"\nendstream endobj\n"
            b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n"
            b"xref\n0 6\n0000000000 65535 f \n"
            b"trailer<< /Size 6 /Root 1 0 R >>\nstartxref\n0\n%%EOF"
        )
        return pdf
    except Exception:
        return md.encode("utf-8")


if __name__ == "__main__":
    ctx = build_report_context({}, {"week_anomalies": []}, {"attribution_chains": []}, "placeholder")
    print("Context keys:", ctx.keys())
