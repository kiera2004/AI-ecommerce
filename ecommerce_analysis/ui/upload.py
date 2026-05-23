"""上传、模板下载与校验 UI"""
from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from config import MAX_UPLOAD_SIZE_MB
from data.data_definitions import (
    ORDER_COLUMN_DOCS,
    PRODUCT_COLUMN_DOCS,
    USER_COLUMN_DOCS,
    empty_template_df,
    get_template_dfs,
)
from utils.data_processor import validate_upload


def _csv_download(df: pd.DataFrame, filename: str) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def render_upload_sidebar() -> dict | None:
    st.sidebar.header("📁 数据上传")
    st.sidebar.caption(f"单文件上限 {MAX_UPLOAD_SIZE_MB}MB，订单须覆盖连续 3 个月")

    st.sidebar.subheader("下载模板")
    c1, c2, c3 = st.sidebar.columns(3)
    u_tpl, p_tpl, o_tpl = get_template_dfs()
    with c1:
        st.download_button("用户", _csv_download(empty_template_df("users"), "users.csv"), "users_template.csv")
    with c2:
        st.download_button("产品", _csv_download(empty_template_df("products"), "products.csv"), "products_template.csv")
    with c3:
        st.download_button("订单", _csv_download(empty_template_df("orders"), "orders.csv"), "orders_template.csv")

    with st.sidebar.expander("📖 上传说明", expanded=False):
        st.markdown("### 用户表 users.csv")
        st.markdown(USER_COLUMN_DOCS)
        st.markdown("### 产品表 products.csv")
        st.markdown(PRODUCT_COLUMN_DOCS)
        st.markdown("### 订单表 orders.csv")
        st.markdown(ORDER_COLUMN_DOCS)

    fu = st.sidebar.file_uploader("users.csv", type=["csv"], key="users")
    fp = st.sidebar.file_uploader("products.csv", type=["csv"], key="products")
    fo = st.sidebar.file_uploader("orders.csv", type=["csv"], key="orders")

    if not (fu and fp and fo):
        return None

    for f, name in [(fu, "users"), (fp, "products"), (fo, "orders")]:
        if f.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            st.sidebar.error(f"{name} 超过 {MAX_UPLOAD_SIZE_MB}MB")
            return None

    users = pd.read_csv(io.BytesIO(fu.getvalue()))
    products = pd.read_csv(io.BytesIO(fp.getvalue()))
    orders = pd.read_csv(io.BytesIO(fo.getvalue()))

    result = validate_upload(users, products, orders)
    if result["ok"]:
        st.sidebar.success("✅ 校验通过")
        for w in result.get("warnings", []):
            st.sidebar.warning(w)
    else:
        for e in result["errors"]:
            st.sidebar.error(e)
        return None

    return result


if __name__ == "__main__":
    st.set_page_config(page_title="Upload Test")
    render_upload_sidebar()
