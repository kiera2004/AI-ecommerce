"""结果展示组件"""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def section_title(title: str, help_text: str = ""):
    st.markdown(f"### {title}")
    if help_text:
        st.caption(help_text)


def _render_metric_table_group(tables: list[dict], section_prefix: str):
    """按指标渲染多张对比表。"""
    if not tables:
        st.info(f"{section_prefix}：数据不足，无法计算")
        return

    week_tables = [t for t in tables if t.get("period_label") == "周对比"]
    month_tables = [t for t in tables if t.get("period_label") == "月对比"]

    if week_tables:
        st.markdown(f"**{section_prefix} · 周对比（最近完整周 vs 上周）**")
        for tbl in week_tables:
            st.markdown(f"##### {tbl['title']}")
            st.dataframe(tbl["data"], use_container_width=True)

    if month_tables:
        st.markdown(f"**{section_prefix} · 月对比（最近完整月 vs 上月）**")
        for tbl in month_tables:
            st.markdown(f"##### {tbl['title']}")
            st.dataframe(tbl["data"], use_container_width=True)


def show_metrics_tabs(metrics: dict[str, Any]):
    tab_u, tab_p, tab_c, tab_co = st.tabs(["👤 用户", "📦 产品", "📣 渠道", "📊 Cohort"])

    with tab_u:
        section_title("用户分层指标", "按 cluster 拆分，每张表一个指标，含当月/上月或当周/上周对比")
        user_tables = (metrics.get("user", {}).get("week_tables") or []) + (
            metrics.get("user", {}).get("month_tables") or []
        )
        _render_metric_table_group(user_tables, "用户层面")

    with tab_p:
        section_title("品类指标", "按 category 拆分，每张表一个指标")
        product_tables = (metrics.get("product", {}).get("week_tables") or []) + (
            metrics.get("product", {}).get("month_tables") or []
        )
        _render_metric_table_group(product_tables, "品类层面")

    with tab_c:
        section_title("渠道指标", metrics.get("channel", {}).get("cac_assumption", ""))
        channel_tables = (metrics.get("channel", {}).get("week_tables") or []) + (
            metrics.get("channel", {}).get("month_tables") or []
        )
        _render_metric_table_group(channel_tables, "渠道层面")

    with tab_co:
        section_title("Cohort 批次分析", "M1-M3 留存、累计 LTV、AOV、折扣依赖、退货、评分")
        co = metrics.get("cohort")
        if co is not None and not co.empty:
            st.dataframe(co, use_container_width=True)
            fig = go.Figure()
            for col in ["M1_retention", "M2_retention", "M3_retention"]:
                if col in co.columns:
                    fig.add_trace(go.Scatter(x=co["cohort_week"], y=co[col], mode="lines+markers", name=col))
            fig.update_layout(title="Cohort 留存曲线", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Cohort 数据不足")


def show_anomaly_results(anomaly: dict[str, Any]):
    section_title("异动检测", "整体汇总层指标变化超过 15%（每个指标仅一条，避免重复）")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**本周异动（最近完整周 vs 上周）**")
        items = anomaly.get("week_anomalies") or []
        if items:
            for i in items:
                st.markdown(f"- {i}")
        else:
            st.markdown("- 暂无")
    with c2:
        st.markdown("**本月异动（最近完整月 vs 上月）**")
        items = anomaly.get("month_anomalies") or []
        if items:
            for i in items:
                st.markdown(f"- {i}")
        else:
            st.markdown("- 暂无")

    section_title("趋势监控")
    for t in anomaly.get("trend_texts") or ["暂无显著趋势"]:
        st.markdown(f"- {t}")
    for fig in anomaly.get("figures") or []:
        st.plotly_chart(fig, use_container_width=True)


def show_root_cause(root: dict[str, Any]):
    period = root.get("compare_period", {})
    if period:
        st.caption(
            f"下钻对比周期：{period.get('previous')} → {period.get('current')} "
            "（订单金额 total_amount 汇总，作为利润/业绩代理指标）"
        )

    section_title("维度下钻", "各维度本月 vs 上月业绩变化，按变化幅度排序")
    drill = root.get("drill_down", {})
    dim_labels = {
        "cluster": "用户分层",
        "channel": "获客渠道",
        "country": "国家",
        "category": "品类",
        "product": "产品",
    }
    for dim, df in drill.items():
        if isinstance(df, pd.DataFrame) and not df.empty:
            with st.expander(f"{dim_labels.get(dim, dim)} · 本月 vs 上月业绩"):
                st.dataframe(df, use_container_width=True)

    section_title("归因链条")
    for chain in root.get("attribution_chains") or []:
        st.markdown(f"- {chain}")

    if root.get("llm_analysis"):
        section_title("AI 根因推理")
        st.markdown(root["llm_analysis"])


def show_strategy(strategy: str):
    section_title("运营策略建议")
    st.markdown(strategy)


def show_growth_report(report_md: str):
    section_title("增长报告")
    st.markdown(report_md)
