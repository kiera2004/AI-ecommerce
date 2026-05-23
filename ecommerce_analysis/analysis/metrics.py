"""指标计算：用户 / 产品 / 渠道 / Cohort"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from utils.data_processor import (
    channel_retention,
    compute_period_metrics,
    estimate_cac,
    merge_user_orders,
    pct_change,
    wow_mom_change,
)
from utils.i18n import LANG_EN, LANG_ZH, metric_labels, t

# Backward-compatible exports (Chinese defaults)
USER_METRIC_LABELS = metric_labels("user", LANG_ZH)
PRODUCT_METRIC_LABELS = metric_labels("product", LANG_ZH)
CHANNEL_METRIC_LABELS = metric_labels("channel", LANG_ZH)


def _safe_mean(s: pd.Series) -> float:
    return float(s.mean()) if len(s) else 0.0


def _cluster_metrics(period_orders: pd.DataFrame, users: pd.DataFrame) -> pd.DataFrame:
    merged = merge_user_orders(users, period_orders)
    if merged.empty:
        return pd.DataFrame()
    total_users = len(users)
    rows = []
    for cluster, grp in merged.groupby("cluster"):
        u_grp = users[users["cluster"] == cluster]
        rows.append(
            {
                "cluster": cluster,
                "share": len(u_grp) / total_users if total_users else 0,
                "active_users": grp["customer_id"].nunique(),
                "avg_discount": _safe_mean(grp["discount_rate"]),
                "avg_rating": _safe_mean(grp["customer_rating"]),
                "return_rate": _safe_mean(grp["returned"]),
                "churn_risk": _safe_mean(u_grp["churned"]),
            }
        )
    return pd.DataFrame(rows)


def _product_metrics(period_orders: pd.DataFrame) -> pd.DataFrame:
    if period_orders.empty:
        return pd.DataFrame()
    g = period_orders.groupby("category").agg(
        revenue=("total_amount", "sum"),
        orders=("order_id", "nunique"),
        aov=("total_amount", "mean"),
        return_rate=("returned", "mean"),
        avg_rating=("customer_rating", "mean"),
        avg_discount=("discount_rate", "mean"),
    )
    return g.reset_index()


def _channel_metrics(period_orders: pd.DataFrame, users: pd.DataFrame, all_orders: pd.DataFrame) -> pd.DataFrame:
    merged = merge_user_orders(users, period_orders)
    if merged.empty:
        return pd.DataFrame()

    first_orders = all_orders.sort_values("order_date").groupby("customer_id").first().reset_index()
    first_merged = first_orders.merge(users, on="customer_id")

    rows = []
    for ch, grp in merged.groupby("acquisition_channel"):
        u_ch = users[users["acquisition_channel"] == ch]
        new_in_period = first_merged[
            (first_merged["acquisition_channel"] == ch)
            & (first_merged["order_date"].isin(grp["order_date"]))
        ]
        first_aov = _safe_mean(new_in_period["total_amount"]) if len(new_in_period) else _safe_mean(grp["total_amount"])
        cac = estimate_cac(first_aov)
        ltv = _safe_mean(u_ch["total_spend"])
        roi = ltv / cac if cac else np.nan
        repurchase = grp.groupby("customer_id").size()
        repurchase_rate = (repurchase > 1).mean() if len(repurchase) else 0

        rows.append(
            {
                "acquisition_channel": ch,
                "new_users": new_in_period["customer_id"].nunique(),
                "first_order_aov": first_aov,
                "repurchase_rate": repurchase_rate,
                "ltv": ltv,
                "cac_estimated": cac,
                "roi_ltv_cac": roi,
                "churn_rate": _safe_mean(u_ch["churned"]),
                "avg_rating": _safe_mean(grp["customer_rating"]),
            }
        )
    ret7 = channel_retention(users, all_orders, 7)
    ret30 = channel_retention(users, all_orders, 30)
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.merge(ret7, on="acquisition_channel", how="left")
        df = df.merge(ret30, on="acquisition_channel", how="left")
    return df


def _compare_frames(cur: pd.DataFrame, prev: pd.DataFrame, key: str, metrics: list[str]) -> pd.DataFrame:
    if cur.empty:
        return pd.DataFrame()
    m = cur.merge(prev, on=key, how="outer", suffixes=("_cur", "_prev"))
    for col in metrics:
        cur_c, prev_c = f"{col}_cur", f"{col}_prev"
        if cur_c in m.columns and prev_c in m.columns:
            m[f"{col}_change_pct"] = m.apply(
                lambda r, c=col: pct_change(r[f"{c}_cur"], r[f"{c}_prev"]), axis=1
            )
    return m


def split_metric_tables(
    compare_df: pd.DataFrame,
    dimension_col: str,
    labels: dict[str, str],
    period_key: str,
    lang: str = LANG_ZH,
) -> list[dict[str, Any]]:
    """按指标拆分为多张表，每张表仅含 dimension + cur + prev + change_pct。"""
    tables: list[dict[str, Any]] = []
    if compare_df is None or compare_df.empty:
        return tables

    period_title = t(f"period.{period_key}", lang)
    for metric, label in labels.items():
        cur_c, prev_c, pct_c = f"{metric}_cur", f"{metric}_prev", f"{metric}_change_pct"
        if cur_c not in compare_df.columns:
            continue
        tbl = compare_df[[dimension_col, cur_c, prev_c, pct_c]].copy()
        tables.append(
            {
                "title": f"{label} ({period_title})" if lang == LANG_EN else f"{label}（{period_title}）",
                "metric": metric,
                "period_key": period_key,
                "dimension_col": dimension_col,
                "data": tbl,
            }
        )
    return tables


def _agg_scalar(cur_df: pd.DataFrame, prev_df: pd.DataFrame, col: str, how: str = "sum") -> tuple[float, float]:
    if how == "sum":
        return float(cur_df[col].sum()) if col in cur_df else 0.0, float(prev_df[col].sum()) if col in prev_df else 0.0
    return _safe_mean(cur_df[col]) if col in cur_df else 0.0, _safe_mean(prev_df[col]) if col in prev_df else 0.0


def build_metrics_flat(
    user_w: pd.DataFrame,
    user_m: pd.DataFrame,
    prod_w: pd.DataFrame,
    prod_m: pd.DataFrame,
    ch_w: pd.DataFrame,
    ch_m: pd.DataFrame,
    lang: str = LANG_ZH,
) -> pd.DataFrame:
    """仅汇总整体层级指标，供异动检测（每个 scope+period+metric 唯一一行）。"""
    flat: list[dict] = []

    def add(scope: str, period: str, metric: str, cur: float, prev: float):
        chg = wow_mom_change(cur, prev)
        flat.append(
            {
                "scope": scope,
                "period_type": period,
                "metric": metric,
                "current": chg["current"],
                "previous": chg["previous"],
                "change_pct": chg["change_pct"],
            }
        )

    user_metrics = list(metric_labels("user", lang).keys())
    product_metrics = list(metric_labels("product", lang).keys())
    channel_metrics = list(metric_labels("channel", lang).keys())

    for period, u_df, p_df, c_df in [
        ("week", user_w, prod_w, ch_w),
        ("month", user_m, prod_m, ch_m),
    ]:
        if u_df is not None and not u_df.empty:
            for m in user_metrics:
                if f"{m}_cur" not in u_df.columns:
                    continue
                how = "sum" if m in ("active_users",) else "mean"
                if m == "share":
                    cur, prev = float(u_df[f"{m}_cur"].sum()), float(u_df[f"{m}_prev"].sum())
                elif how == "sum":
                    cur, prev = float(u_df[f"{m}_cur"].sum()), float(u_df[f"{m}_prev"].sum())
                else:
                    cur, prev = _safe_mean(u_df[f"{m}_cur"]), _safe_mean(u_df[f"{m}_prev"])
                add("user", period, m, cur, prev)

        if p_df is not None and not p_df.empty:
            for m in product_metrics:
                if f"{m}_cur" not in p_df.columns:
                    continue
                if m in ("revenue", "orders"):
                    cur, prev = float(p_df[f"{m}_cur"].sum()), float(p_df[f"{m}_prev"].sum())
                else:
                    cur, prev = _safe_mean(p_df[f"{m}_cur"]), _safe_mean(p_df[f"{m}_prev"])
                add("product", period, m, cur, prev)

        if c_df is not None and not c_df.empty:
            for m in channel_metrics:
                if f"{m}_cur" not in c_df.columns:
                    continue
                if m == "new_users":
                    cur, prev = float(c_df[f"{m}_cur"].sum()), float(c_df[f"{m}_prev"].sum())
                else:
                    cur, prev = _safe_mean(c_df[f"{m}_cur"]), _safe_mean(c_df[f"{m}_prev"])
                add("channel", period, m, cur, prev)

    return pd.DataFrame(flat)


def compute_all_metrics(
    users: pd.DataFrame,
    products: pd.DataFrame,
    orders: pd.DataFrame,
    lang: str = LANG_ZH,
) -> dict[str, Any]:
    base = compute_period_metrics(users, products, orders)

    user_w_cur = _cluster_metrics(base["week"]["current"], users)
    user_w_prev = _cluster_metrics(base["week"]["prev"], users)
    user_m_cur = _cluster_metrics(base["month"]["current"], users)
    user_m_prev = _cluster_metrics(base["month"]["prev"], users)

    prod_w_cur = _product_metrics(base["week"]["current"])
    prod_w_prev = _product_metrics(base["week"]["prev"])
    prod_m_cur = _product_metrics(base["month"]["current"])
    prod_m_prev = _product_metrics(base["month"]["prev"])

    ch_w_cur = _channel_metrics(base["week"]["current"], users, orders)
    ch_w_prev = _channel_metrics(base["week"]["prev"], users, orders)
    ch_m_cur = _channel_metrics(base["month"]["current"], users, orders)
    ch_m_prev = _channel_metrics(base["month"]["prev"], users, orders)

    user_lbl = metric_labels("user", lang)
    product_lbl = metric_labels("product", lang)
    channel_lbl = metric_labels("channel", lang)
    user_metrics = list(user_lbl.keys())
    product_metrics = list(product_lbl.keys())
    channel_metrics = list(channel_lbl.keys())

    user_week = _compare_frames(user_w_cur, user_w_prev, "cluster", user_metrics)
    user_month = _compare_frames(user_m_cur, user_m_prev, "cluster", user_metrics)
    prod_week = _compare_frames(prod_w_cur, prod_w_prev, "category", product_metrics)
    prod_month = _compare_frames(prod_m_cur, prod_m_prev, "category", product_metrics)
    ch_week = _compare_frames(ch_w_cur, ch_w_prev, "acquisition_channel", channel_metrics)
    ch_month = _compare_frames(ch_m_cur, ch_m_prev, "acquisition_channel", channel_metrics)

    metrics_flat = build_metrics_flat(user_week, user_month, prod_week, prod_month, ch_week, ch_month, lang)

    return {
        "periods": base["periods"],
        "user": {
            "week": user_week,
            "month": user_month,
            "week_tables": split_metric_tables(user_week, "cluster", user_lbl, "week", lang),
            "month_tables": split_metric_tables(user_month, "cluster", user_lbl, "month", lang),
        },
        "product": {
            "week": prod_week,
            "month": prod_month,
            "week_tables": split_metric_tables(prod_week, "category", product_lbl, "week", lang),
            "month_tables": split_metric_tables(prod_month, "category", product_lbl, "month", lang),
        },
        "channel": {
            "week": ch_week,
            "month": ch_month,
            "week_tables": split_metric_tables(ch_week, "acquisition_channel", channel_lbl, "week", lang),
            "month_tables": split_metric_tables(ch_month, "acquisition_channel", channel_lbl, "month", lang),
            "cac_assumption": t("cac.assumption", lang),
        },
        "cohort": base["cohort"],
        "metrics_flat": metrics_flat,
        "products_table": products,
        "metric_labels": {
            "user": user_lbl,
            "product": product_lbl,
            "channel": channel_lbl,
        },
        "lang": lang,
    }


if __name__ == "__main__":
    import pandas as pd
    from utils.data_processor import validate_upload

    u = pd.read_csv("sample_data/users.csv")
    p = pd.read_csv("sample_data/products.csv")
    o = pd.read_csv("sample_data/orders.csv")
    r = validate_upload(u, p, o)
    m = compute_all_metrics(r["users"], r["products"], r["orders"])
    print("user week tables:", len(m["user"]["week_tables"]))
    print("user month tables:", len(m["user"]["month_tables"]))
    print("metrics_flat rows:", len(m["metrics_flat"]))
