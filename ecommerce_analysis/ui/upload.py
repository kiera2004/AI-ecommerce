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
)
from utils.data_processor import validate_upload
from utils.i18n import column_docs, get_lang, t


def _csv_download(df: pd.DataFrame, filename: str) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def _get_column_docs(lang: str) -> tuple[str, str, str]:
    try:
        return column_docs(lang)
    except (KeyError, TypeError):
        return USER_COLUMN_DOCS, PRODUCT_COLUMN_DOCS, ORDER_COLUMN_DOCS


def render_upload_sidebar() -> dict | None:
    lang = get_lang()
    st.sidebar.header(t("upload.header", lang))
    st.sidebar.caption(t("upload.caption", lang, max_mb=MAX_UPLOAD_SIZE_MB))

    st.sidebar.subheader(t("upload.download_templates", lang))
    c1, c2, c3 = st.sidebar.columns(3)
    with c1:
        st.download_button(
            t("upload.users", lang),
            _csv_download(empty_template_df("users"), "users.csv"),
            "users_template.csv",
        )
    with c2:
        st.download_button(
            t("upload.products", lang),
            _csv_download(empty_template_df("products"), "products.csv"),
            "products_template.csv",
        )
    with c3:
        st.download_button(
            t("upload.orders", lang),
            _csv_download(empty_template_df("orders"), "orders.csv"),
            "orders_template.csv",
        )

    fu = st.sidebar.file_uploader("users.csv", type=["csv"], key="users")
    fp = st.sidebar.file_uploader("products.csv", type=["csv"], key="products")
    fo = st.sidebar.file_uploader("orders.csv", type=["csv"], key="orders")

    user_docs, product_docs, order_docs = _get_column_docs(lang)
    with st.sidebar.expander(t("upload.instructions", lang), expanded=False):
        st.markdown(t("upload.users_table", lang))
        st.markdown(user_docs)
        st.markdown(t("upload.products_table", lang))
        st.markdown(product_docs)
        st.markdown(t("upload.orders_table", lang))
        st.markdown(order_docs)

    if not (fu and fp and fo):
        return None

    for f, name in [(fu, "users"), (fp, "products"), (fo, "orders")]:
        if f.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            st.sidebar.error(t("upload.file_too_large", lang, name=name, max_mb=MAX_UPLOAD_SIZE_MB))
            return None

    users = pd.read_csv(io.BytesIO(fu.getvalue()))
    products = pd.read_csv(io.BytesIO(fp.getvalue()))
    orders = pd.read_csv(io.BytesIO(fo.getvalue()))

    result = validate_upload(users, products, orders)
    if result["ok"]:
        st.sidebar.success(t("upload.validation_ok", lang))
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
