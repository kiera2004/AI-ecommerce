"""结果展示组件"""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.i18n import (
    LANG_ZH,
    dim_label,
    localize_cohort_table,
    localize_compare_table,
    localize_drill_table,
    t,
)


def section_title(title: str, help_text: str = ""):
    st.markdown(f"### {title}")
    if help_text:
        st.caption(help_text)


def _render_metric_table_group(tables: list[dict], section_prefix: str, lang: str = LANG_ZH):
    """按指标渲染多张对比表。"""
    if not tables:
        st.info(t("metrics.insufficient", lang, prefix=section_prefix))
        return

    week_tables = [tbl for tbl in tables if tbl.get("period_key") == "week"]
    month_tables = [tbl for tbl in tables if tbl.get("period_key") == "month"]

    if week_tables:
        st.markdown(t("metrics.week_section", lang, prefix=section_prefix))
        for tbl in week_tables:
            st.markdown(f"##### {tbl['title']}")
            display_df = localize_compare_table(
                tbl["data"], tbl["dimension_col"], tbl["metric"], lang
            )
            st.dataframe(display_df, use_container_width=True)

    if month_tables:
        st.markdown(t("metrics.month_section", lang, prefix=section_prefix))
        for tbl in month_tables:
            st.markdown(f"##### {tbl['title']}")
            display_df = localize_compare_table(
                tbl["data"], tbl["dimension_col"], tbl["metric"], lang
            )
            st.dataframe(display_df, use_container_width=True)


def show_metrics_tabs(metrics: dict[str, Any], lang: str = LANG_ZH):
    tab_u, tab_p, tab_c, tab_co = st.tabs([
        t("tab.users", lang),
        t("tab.products", lang),
        t("tab.channels", lang),
        t("tab.cohort", lang),
    ])

    with tab_u:
        section_title(t("metrics.user_title", lang), t("metrics.user_help", lang))
        user_tables = (metrics.get("user", {}).get("week_tables") or []) + (
            metrics.get("user", {}).get("month_tables") or []
        )
        _render_metric_table_group(user_tables, t("metrics.user_level", lang), lang)

    with tab_p:
        section_title(t("metrics.product_title", lang), t("metrics.product_help", lang))
        product_tables = (metrics.get("product", {}).get("week_tables") or []) + (
            metrics.get("product", {}).get("month_tables") or []
        )
        _render_metric_table_group(product_tables, t("metrics.product_level", lang), lang)

    with tab_c:
        section_title(t("metrics.channel_title", lang), metrics.get("channel", {}).get("cac_assumption", ""))
        channel_tables = (metrics.get("channel", {}).get("week_tables") or []) + (
            metrics.get("channel", {}).get("month_tables") or []
        )
        _render_metric_table_group(channel_tables, t("metrics.channel_level", lang), lang)

    with tab_co:
        section_title(t("metrics.cohort_title", lang), t("metrics.cohort_help", lang))
        co = metrics.get("cohort")
        if co is not None and not co.empty:
            st.dataframe(localize_cohort_table(co, lang), use_container_width=True)
            fig = go.Figure()
            for col in ["M1_retention", "M2_retention", "M3_retention"]:
                if col in co.columns:
                    label = "M1 Retention" if col == "M1_retention" and lang != LANG_ZH else col
                    if lang == LANG_ZH:
                        label = {"M1_retention": "M1 留存", "M2_retention": "M2 留存", "M3_retention": "M3 留存"}.get(col, col)
                    fig.add_trace(go.Scatter(x=co["cohort_week"], y=co[col], mode="lines+markers", name=label))
            fig.update_layout(title=t("metrics.cohort_chart", lang), template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t("metrics.cohort_empty", lang))


def show_anomaly_results(anomaly: dict[str, Any], lang: str = LANG_ZH):
    section_title(t("anomaly.title", lang), t("anomaly.help", lang))
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(t("anomaly.week_title", lang))
        items = anomaly.get("week_anomalies") or []
        if items:
            for i in items:
                st.markdown(f"- {i}")
        else:
            st.markdown(t("anomaly.none", lang))
    with c2:
        st.markdown(t("anomaly.month_title", lang))
        items = anomaly.get("month_anomalies") or []
        if items:
            for i in items:
                st.markdown(f"- {i}")
        else:
            st.markdown(t("anomaly.none", lang))

    section_title(t("anomaly.trends_title", lang))
    for text in anomaly.get("trend_texts") or [t("anomaly.no_trend", lang)]:
        st.markdown(f"- {text}")
    for fig in anomaly.get("figures") or []:
        st.plotly_chart(fig, use_container_width=True)


def show_root_cause(root: dict[str, Any], lang: str = LANG_ZH):
    period = root.get("compare_period", {})
    if period:
        st.caption(
            t("root.period_caption", lang, prev=period.get("previous"), cur=period.get("current"))
        )

    section_title(t("root.drill_title", lang), t("root.drill_help", lang))
    drill = root.get("drill_down", {})
    for dim, df in drill.items():
        if isinstance(df, pd.DataFrame) and not df.empty:
            with st.expander(t("root.expander", lang, dim=dim_label(dim, lang))):
                st.dataframe(localize_drill_table(df, lang), use_container_width=True)

    section_title(t("root.attribution", lang))
    for chain in root.get("attribution_chains") or []:
        st.markdown(f"- {chain}")

    if root.get("llm_analysis"):
        section_title(t("root.ai_analysis", lang))
        st.markdown(root["llm_analysis"])


def show_strategy(strategy: str, lang: str = LANG_ZH):
    section_title(t("strategy.title", lang))
    st.markdown(strategy)


def show_growth_report(report_md: str, lang: str = LANG_ZH):
    section_title(t("report.title", lang))
    st.markdown(report_md)
