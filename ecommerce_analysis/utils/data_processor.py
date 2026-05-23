"""数据清洗、校验与基础指标计算"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from config import REQUIRED_ORDER_MONTHS
from data.data_definitions import ORDER_COLUMNS, PRODUCT_COLUMNS, USER_COLUMNS


def _check_columns(df: pd.DataFrame, expected: dict, name: str) -> list[str]:
    errors: list[str] = []
    missing = set(expected) - set(df.columns)
    extra = set(df.columns) - set(expected)
    if missing:
        errors.append(f"{name} 缺少列: {sorted(missing)}")
    if extra:
        errors.append(f"{name} 多余列: {sorted(extra)}")
    return errors


def _coerce_types(df: pd.DataFrame, schema: dict) -> pd.DataFrame:
    out = df.copy()
    for col, dtype in schema.items():
        if col not in out.columns:
            continue
        if dtype == "str":
            out[col] = out[col].astype(str)
        elif dtype == "int":
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0).astype(int)
        elif dtype == "float":
            out[col] = pd.to_numeric(out[col], errors="coerce").astype(float)
    return out


def parse_orders(orders: pd.DataFrame) -> pd.DataFrame:
    df = _coerce_types(orders, ORDER_COLUMNS)
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df = df.dropna(subset=["order_date"])
    df["order_week"] = df["order_date"].dt.to_period("W").apply(lambda p: p.start_time)
    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["is_weekend"] = df["order_date"].dt.dayofweek >= 5
    return df


def validate_three_month_span(orders: pd.DataFrame) -> tuple[bool, str]:
    if orders.empty:
        return False, "订单表为空"
    dates = orders["order_date"]
    months = sorted({(d.year, d.month) for d in dates})
    if len(months) != REQUIRED_ORDER_MONTHS:
        return False, (
            f"订单日期须恰好覆盖 {REQUIRED_ORDER_MONTHS} 个连续自然月，"
            f"当前检测到 {len(months)} 个月: {months}"
        )
    for i in range(1, len(months)):
        y1, m1 = months[i - 1]
        y2, m2 = months[i]
        expected_m = m1 + 1 if m1 < 12 else 1
        expected_y = y1 if m1 < 12 else y1 + 1
        if (y2, m2) != (expected_y, expected_m):
            return False, f"月份不连续: {months}"
    span = f"{months[0][0]}-{months[0][1]:02d} 至 {months[-1][0]}-{months[-1][1]:02d}"
    return True, f"日期范围校验通过，覆盖 {span}"


def validate_upload(
    users: pd.DataFrame,
    products: pd.DataFrame,
    orders: pd.DataFrame,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    for df, schema, name in [
        (users, USER_COLUMNS, "users"),
        (products, PRODUCT_COLUMNS, "products"),
        (orders, ORDER_COLUMNS, "orders"),
    ]:
        errors.extend(_check_columns(df, schema, name))

    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}

    users_c = _coerce_types(users, USER_COLUMNS)
    products_c = _coerce_types(products, PRODUCT_COLUMNS)
    orders_c = parse_orders(orders)

    ok_span, span_msg = validate_three_month_span(orders_c)
    if not ok_span:
        errors.append(span_msg)
    else:
        warnings.append(span_msg)

    order_users = set(orders_c["customer_id"])
    user_ids = set(users_c["customer_id"])
    orphan = order_users - user_ids
    if orphan:
        warnings.append(f"订单中有 {len(orphan)} 个 customer_id 不在用户表")

    if not set(users_c["churned"].unique()).issubset({0, 1}):
        errors.append("users.churned 必须为 0 或 1")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "users": users_c,
        "products": products_c,
        "orders": orders_c,
    }


def get_reference_periods(orders: pd.DataFrame) -> dict[str, Any]:
    max_date = orders["order_date"].max()
    week_end = max_date - pd.Timedelta(days=max_date.weekday() + 1)
    current_week_start = week_end - pd.Timedelta(days=6)
    prev_week_start = current_week_start - pd.Timedelta(days=7)
    prev_week_end = current_week_start - pd.Timedelta(days=1)

    months = sorted(orders["order_month"].unique())
    current_month = months[-1]
    prev_month = months[-2] if len(months) >= 2 else months[-1]

    return {
        "current_week": (current_week_start, week_end),
        "prev_week": (prev_week_start, prev_week_end),
        "current_month": current_month,
        "prev_month": prev_month,
        "all_months": months,
    }


def filter_period(orders: pd.DataFrame, start, end=None) -> pd.DataFrame:
    if end is not None:
        return orders[(orders["order_date"] >= start) & (orders["order_date"] <= end)]
    return orders[orders["order_month"] == start]


def merge_user_orders(users: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    return orders.merge(users, on="customer_id", how="left")


def pct_change(new: float, old: float) -> float:
    if old == 0 or np.isnan(old):
        return np.nan if new == 0 else np.inf
    return (new - old) / abs(old)


def wow_mom_change(current: float, previous: float) -> dict[str, float]:
    return {
        "current": current,
        "previous": previous,
        "change": current - previous,
        "change_pct": pct_change(current, previous),
    }


def channel_retention(users: pd.DataFrame, orders: pd.DataFrame, days: int) -> pd.DataFrame:
    first = orders.sort_values("order_date").groupby("customer_id").first().reset_index()
    first = first.merge(users[["customer_id", "acquisition_channel"]], on="customer_id")
    rows = []
    for ch, grp in first.groupby("acquisition_channel"):
        total = len(grp)
        retained = 0
        for _, row in grp.iterrows():
            cid, fd = row["customer_id"], row["order_date"]
            later = orders[
                (orders["customer_id"] == cid)
                & (orders["order_date"] > fd)
                & (orders["order_date"] <= fd + pd.Timedelta(days=days))
            ]
            if len(later) > 0:
                retained += 1
        rows.append({"acquisition_channel": ch, f"retention_{days}d": retained / total if total else 0})
    return pd.DataFrame(rows)


def estimate_cac(first_order_aov: float) -> float:
    return first_order_aov * 0.35


def build_cohort_table(orders: pd.DataFrame, users: pd.DataFrame) -> pd.DataFrame:
    first = (
        orders.sort_values("order_date")
        .groupby("customer_id")
        .agg(first_date=("order_date", "min"))
        .reset_index()
    )
    first["cohort_week"] = first["first_date"].dt.to_period("W").astype(str)
    merged = orders.merge(first, on="customer_id")
    merged["weeks_since_first"] = (merged["order_date"] - merged["first_date"]).dt.days // 7

    cohorts = []
    for cw, grp in merged.groupby("cohort_week"):
        customers = grp["customer_id"].nunique()
        row: dict[str, Any] = {"cohort_week": cw, "cohort_size": customers}
        for m in (1, 2, 3):
            active = grp[grp["weeks_since_first"].between((m - 1) * 4 + 1, m * 4)]["customer_id"].nunique()
            row[f"M{m}_retention"] = active / customers if customers else 0
        row["cumulative_ltv"] = grp.groupby("customer_id")["total_amount"].sum().mean()
        row["aov"] = grp["total_amount"].mean()
        row["avg_discount"] = grp["discount_rate"].mean()
        row["return_rate"] = grp["returned"].mean()
        row["avg_rating"] = grp["customer_rating"].mean()
        cohorts.append(row)
    return pd.DataFrame(cohorts).sort_values("cohort_week")


def compute_period_metrics(users: pd.DataFrame, products: pd.DataFrame, orders: pd.DataFrame) -> dict[str, Any]:
    periods = get_reference_periods(orders)
    merged = merge_user_orders(users, orders)

    def period_slice(kind: str, which: str) -> pd.DataFrame:
        if kind == "week":
            s, e = periods[which + "_week"]
            return filter_period(orders, s, e)
        return filter_period(orders, periods[which + "_month"])

    return {
        "periods": periods,
        "merged": merged,
        "week": {"current": period_slice("week", "current"), "prev": period_slice("week", "prev")},
        "month": {"current": period_slice("month", "current"), "prev": period_slice("month", "prev")},
        "cohort": build_cohort_table(orders, users),
    }
