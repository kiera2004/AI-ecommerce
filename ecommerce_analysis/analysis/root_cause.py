"""根因分析：维度下钻（本月 vs 上月营收）+ 假设验证 + LLM"""
from __future__ import annotations

from typing import Any

import pandas as pd

from utils.data_processor import (
    filter_period,
    get_reference_periods,
    merge_user_orders,
    pct_change,
)
from utils.llm_client import call_deepseek, load_prompt


def _month_slices(orders: pd.DataFrame, users: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str, str]:
    periods = get_reference_periods(orders)
    cur_label = periods["current_month"]
    prev_label = periods["prev_month"]
    cur_orders = filter_period(orders, cur_label)
    prev_orders = filter_period(orders, prev_label)
    return cur_orders, prev_orders, cur_label, prev_label


def _revenue_by_dims(df: pd.DataFrame, users: pd.DataFrame, dims: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=dims + ["revenue"])
    if "cluster" in dims or "acquisition_channel" in dims or "country" in dims:
        merged = merge_user_orders(users, df)
        src = merged
    else:
        src = df
    missing = [d for d in dims if d not in src.columns]
    if missing:
        return pd.DataFrame(columns=dims + ["revenue"])
    return src.groupby(dims, as_index=False)["total_amount"].sum().rename(columns={"total_amount": "revenue"})


def drill_down(orders: pd.DataFrame, users: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    各维度对比：最近完整月 vs 上月 的营收（total_amount 汇总，作为利润/业绩代理指标）。
    按变化幅度排序，定位问题细分群体。
    """
    cur_orders, prev_orders, cur_label, prev_label = _month_slices(orders, users)
    results: dict[str, pd.DataFrame] = {}

    dimensions = [
        ("cluster", ["cluster"]),
        ("channel", ["acquisition_channel"]),
        ("country", ["country"]),
        ("category", ["category"]),
        ("product", ["category", "product_name"]),
    ]

    for label, dims in dimensions:
        cur = _revenue_by_dims(cur_orders, users, dims)
        prev = _revenue_by_dims(prev_orders, users, dims)
        if cur.empty and prev.empty:
            continue

        m = cur.merge(prev, on=dims, how="outer", suffixes=("_cur", "_prev")).fillna(0)
        m = m.rename(columns={"revenue_cur": "revenue_cur", "revenue_prev": "revenue_prev"})
        m["revenue_change"] = m["revenue_cur"] - m["revenue_prev"]
        m["revenue_change_pct"] = m.apply(
            lambda r: pct_change(r["revenue_cur"], r["revenue_prev"]), axis=1
        )
        m["current_month"] = cur_label
        m["prev_month"] = prev_label
        results[label] = m.sort_values("revenue_change_pct", key=lambda s: s.abs(), ascending=False).head(15)

    return results


def rule_based_attribution(
    drill_tables: dict[str, pd.DataFrame],
    merged: pd.DataFrame,
    cur_label: str,
    prev_label: str,
) -> list[str]:
    chains: list[str] = [f"对比周期：{prev_label} → {cur_label}（营收维度）"]

    for dim, label in [
        ("channel", "渠道"),
        ("category", "品类"),
        ("cluster", "用户分层"),
        ("country", "国家"),
    ]:
        if dim not in drill_tables or drill_tables[dim].empty:
            continue
        top = drill_tables[dim].iloc[0]
        dim_cols = [c for c in top.index if c not in (
            "revenue_cur", "revenue_prev", "revenue_change", "revenue_change_pct",
            "current_month", "prev_month",
        )]
        dim_val = " / ".join(str(top[c]) for c in dim_cols)
        chains.append(
            f"{label}维度 [{dim_val}]：营收 {top['revenue_prev']:.2f} → {top['revenue_cur']:.2f} "
            f"({top['revenue_change_pct']:+.1%})，变化额 {top['revenue_change']:.2f}"
        )

    if not merged.empty:
        disc = merged.groupby(merged["order_date"].dt.to_period("M"))["discount_rate"].mean()
        if len(disc) >= 2 and disc.iloc[-1] - disc.iloc[-2] > 0.05:
            chains.append("验证：最近月平均折扣率上升，可能与营收/毛利波动相关。")
        ret = merged.groupby(merged["order_date"].dt.to_period("M"))["returned"].mean()
        if len(ret) >= 2 and ret.iloc[-1] - ret.iloc[-2] > 0.03:
            chains.append("验证：最近月退货率上升，需排查产品质量或预期管理。")

    return chains


def run_root_cause(
    orders: pd.DataFrame,
    users: pd.DataFrame,
    anomaly_result: dict[str, Any],
    use_llm: bool = True,
) -> dict[str, Any]:
    _, _, cur_label, prev_label = _month_slices(orders, users)
    drill_tables = drill_down(orders, users)
    merged = merge_user_orders(users, orders)
    attribution = rule_based_attribution(drill_tables, merged, cur_label, prev_label)

    llm_text = ""
    if use_llm:
        try:
            prompt_tpl = load_prompt("root_cause_prompt.txt")
            data_blob = {
                "compare_period": f"{prev_label} vs {cur_label}",
                "week_anomalies": anomaly_result.get("week_anomalies", []),
                "month_anomalies": anomaly_result.get("month_anomalies", []),
                "drill_down": {k: v.head(5).to_dict("records") for k, v in drill_tables.items()},
                "rule_attribution": attribution,
            }
            system = prompt_tpl.format(data=str(data_blob))
            llm_text = call_deepseek(system, "请基于本月vs上月各维度营收下钻结果，输出根因分析结论与验证链条。")
        except Exception as e:
            llm_text = f"（LLM 未调用: {e}）"

    return {
        "drill_down": drill_tables,
        "attribution_chains": attribution,
        "llm_analysis": llm_text,
        "compare_period": {"current": cur_label, "previous": prev_label},
    }


if __name__ == "__main__":
    print("Root cause module ready")
