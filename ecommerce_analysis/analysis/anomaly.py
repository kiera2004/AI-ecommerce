"""异动检测与趋势监控"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from config import ANOMALY_THRESHOLD
from analysis.metrics import CHANNEL_METRIC_LABELS, PRODUCT_METRIC_LABELS, USER_METRIC_LABELS

SCOPE_LABELS = {"user": "用户", "product": "产品", "channel": "渠道"}
METRIC_LABELS = {**USER_METRIC_LABELS, **PRODUCT_METRIC_LABELS, **CHANNEL_METRIC_LABELS}


def _is_anomaly(change_pct: float, threshold: float = ANOMALY_THRESHOLD) -> bool:
    if change_pct is None or (isinstance(change_pct, float) and np.isnan(change_pct)):
        return False
    if np.isinf(change_pct):
        return True
    return abs(change_pct) >= threshold


def _format_anomaly_line(row: pd.Series) -> str:
    scope = SCOPE_LABELS.get(row["scope"], row["scope"])
    metric = METRIC_LABELS.get(row["metric"], row["metric"])
    pct = row["change_pct"]
    return (
        f"[{scope}] {metric}: "
        f"{row['previous']:.4f} → {row['current']:.4f} "
        f"({pct:+.1%})"
    )


def detect_anomalies(metrics_result: dict[str, Any]) -> dict[str, Any]:
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
                bucket.append(_format_anomaly_line(row))

    return {
        "week_anomalies": week_lines,
        "month_anomalies": month_lines,
    }


def monitor_trends(orders: pd.DataFrame, cohort: pd.DataFrame) -> dict[str, Any]:
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
                texts.append(f"连续趋势：周营收第 {i - 1}-{i + 1} 周同向变化")
                break

        mean, std = rev.mean(), rev.std()
        if std > 0 and abs(rev[-1] - mean) > 2 * std:
            texts.append(f"历史对比：最近一周营收 {rev[-1]:.0f} 偏离3月均值的2σ以上")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weekly["order_date"], y=weekly["revenue"], mode="lines+markers", name="周营收"))
    fig.update_layout(title="周营收趋势", template="plotly_white")
    figures.append(fig)

    if not cohort.empty and "M1_retention" in cohort.columns:
        m1 = cohort["M1_retention"].values
        if len(m1) >= 3 and all(m1[i] < m1[i - 1] for i in range(len(m1) - 2, len(m1))):
            texts.append("Cohort 逐批恶化：最近3批 M1 留存连续下降")

        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(x=cohort["cohort_week"], y=cohort["M1_retention"], mode="lines+markers", name="M1留存")
        )
        fig2.update_layout(title="Cohort M1 留存趋势", template="plotly_white")
        figures.append(fig2)

    return {"trend_texts": texts, "figures": figures}


def run_anomaly_analysis(metrics_result: dict[str, Any], orders: pd.DataFrame) -> dict[str, Any]:
    anomalies = detect_anomalies(metrics_result)
    trends = monitor_trends(orders, metrics_result.get("cohort", pd.DataFrame()))
    return {**anomalies, **trends}


if __name__ == "__main__":
    print("Anomaly module ready, threshold:", ANOMALY_THRESHOLD)
