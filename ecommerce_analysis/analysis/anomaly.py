"""异动检测与趋势监控"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from config import ANOMALY_THRESHOLD
from utils.i18n import LANG_ZH, all_metric_labels, scope_label, t


def _is_anomaly(change_pct: float, threshold: float = ANOMALY_THRESHOLD) -> bool:
    if change_pct is None or (isinstance(change_pct, float) and np.isnan(change_pct)):
        return False
    if np.isinf(change_pct):
        return True
    return abs(change_pct) >= threshold


def _format_anomaly_line(row: pd.Series, lang: str = LANG_ZH) -> str:
    labels = all_metric_labels(lang)
    scope = scope_label(row["scope"], lang)
    metric = labels.get(row["metric"], row["metric"])
    pct = row["change_pct"]
    return (
        f"[{scope}] {metric}: "
        f"{row['previous']:.4f} → {row['current']:.4f} "
        f"({pct:+.1%})"
    )


def detect_anomalies(metrics_result: dict[str, Any], lang: str = LANG_ZH) -> dict[str, Any]:
    """
    异动仅基于 metrics_flat（整体汇总层，每个 scope+period+metric 唯一）。
    不再从细分对比表逐行扫描，避免同一指标出现多个不同百分比。
    """
    flat = metrics_result.get("metrics_flat", pd.DataFrame())
    week_lines: list[str] = []
    month_lines: list[str] = []

    if flat.empty:
        return {"week_anomalies": [], "month_anomalies": []}

    for period_type, bucket in [("week", week_lines), ("month", month_lines)]:
        sub = flat[flat["period_type"] == period_type]
        for _, row in sub.iterrows():
            if _is_anomaly(row.get("change_pct", 0)):
                bucket.append(_format_anomaly_line(row, lang))

    return {
        "week_anomalies": week_lines,
        "month_anomalies": month_lines,
    }


def monitor_trends(orders: pd.DataFrame, cohort: pd.DataFrame, lang: str = LANG_ZH) -> dict[str, Any]:
    texts: list[str] = []
    figures: list[go.Figure] = []

    weekly = (
        orders.groupby(orders["order_date"].dt.to_period("W"))
        .agg(revenue=("total_amount", "sum"), orders=("order_id", "nunique"))
        .reset_index()
    )
    weekly["order_date"] = weekly["order_date"].astype(str)

    if len(weekly) >= 3:
        rev = weekly["revenue"].values
        for i in range(2, len(rev)):
            if (rev[i] > rev[i - 1] > rev[i - 2]) or (rev[i] < rev[i - 1] < rev[i - 2]):
                texts.append(
                    t("trend.consecutive", lang, start=i - 1, end=i + 1)
                )
                break

        mean, std = rev.mean(), rev.std()
        if std > 0 and abs(rev[-1] - mean) > 2 * std:
            texts.append(t("trend.sigma", lang, value=rev[-1]))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=weekly["order_date"],
            y=weekly["revenue"],
            mode="lines+markers",
            name=t("chart.weekly_revenue", lang),
        )
    )
    fig.update_layout(title=t("chart.weekly_revenue_title", lang), template="plotly_white")
    figures.append(fig)

    if not cohort.empty and "M1_retention" in cohort.columns:
        m1 = cohort["M1_retention"].values
        if len(m1) >= 3 and all(m1[i] < m1[i - 1] for i in range(len(m1) - 2, len(m1))):
            texts.append(t("trend.cohort_decline", lang))

        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=cohort["cohort_week"],
                y=cohort["M1_retention"],
                mode="lines+markers",
                name=t("chart.m1_retention", lang),
            )
        )
        fig2.update_layout(title=t("chart.m1_retention_title", lang), template="plotly_white")
        figures.append(fig2)

    return {"trend_texts": texts, "figures": figures}


def run_anomaly_analysis(
    metrics_result: dict[str, Any],
    orders: pd.DataFrame,
    lang: str = LANG_ZH,
) -> dict[str, Any]:
    anomalies = detect_anomalies(metrics_result, lang)
    trends = monitor_trends(orders, metrics_result.get("cohort", pd.DataFrame()), lang)
    return {**anomalies, **trends}


if __name__ == "__main__":
    print("Anomaly module ready, threshold:", ANOMALY_THRESHOLD)
