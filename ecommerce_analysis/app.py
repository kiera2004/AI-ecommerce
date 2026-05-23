"""
电商销售数据分析 — Streamlit 主应用
启动: streamlit run app.py
"""
from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from analysis.anomaly import run_anomaly_analysis
from analysis.metrics import compute_all_metrics
from analysis.root_cause import run_root_cause
from report.growth_report import (
    build_report_context,
    export_markdown_bytes,
    export_simple_pdf_bytes,
    generate_growth_report,
    report_to_markdown,
)
from report.strategy import generate_strategy
from ui.display import (
    show_anomaly_results,
    show_growth_report,
    show_metrics_tabs,
    show_root_cause,
    show_strategy,
)
from ui.upload import render_upload_sidebar

load_dotenv()

st.set_page_config(
    page_title="Ecommerce Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 电商销售数据分析")
st.caption("指标监控 · 异动检测 · 根因分析 · 策略与增长报告")

validated = render_upload_sidebar()

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if validated and st.sidebar.button("🚀 开始分析", type="primary", use_container_width=True):
    with st.spinner("正在计算指标与分析…"):
        users = validated["users"]
        products = validated["products"]
        orders = validated["orders"]

        metrics = compute_all_metrics(users, products, orders)
        anomaly = run_anomaly_analysis(metrics, orders)
        root = run_root_cause(orders, users, anomaly, use_llm=bool(__import__("os").getenv("DEEPSEEK_API_KEY")))

        strategy = ""
        report = ""
        if __import__("os").getenv("DEEPSEEK_API_KEY"):
            try:
                with st.spinner("生成运营策略…"):
                    strategy = generate_strategy(root, metrics_summary=str(metrics.get("metrics_flat", "")))
                with st.spinner("生成增长报告…"):
                    ctx = build_report_context(metrics, anomaly, root, strategy)
                    report = generate_growth_report(ctx)
            except Exception as e:
                strategy = f"策略生成失败: {e}"
                report = f"报告生成失败: {e}"
        else:
            strategy = "（未配置 DEEPSEEK_API_KEY，跳过 LLM 策略生成）"
            report = report_to_markdown(
                "## 核心摘要\n请配置 DEEPSEEK_API_KEY 以生成完整 AI 报告。\n\n"
                + "\n".join(anomaly.get("month_anomalies", []))
            )

        st.session_state.update(
            {
                "analysis_done": True,
                "metrics": metrics,
                "anomaly": anomaly,
                "root": root,
                "strategy": strategy,
                "report_md": report_to_markdown(report if report.startswith("#") else report),
            }
        )

if st.session_state.get("analysis_done"):
    metrics = st.session_state["metrics"]
    anomaly = st.session_state["anomaly"]
    root = st.session_state["root"]
    strategy = st.session_state["strategy"]
    report_md = st.session_state["report_md"]

    t1, t2, t3, t4, t5 = st.tabs(
        ["📊 指标变化", "⚠️ 异动与趋势", "🔍 根因分析", "💡 策略建议", "📄 增长报告"]
    )

    with t1:
        show_metrics_tabs(metrics)
    with t2:
        show_anomaly_results(anomaly)
    with t3:
        show_root_cause(root)
    with t4:
        show_strategy(strategy)
    with t5:
        show_growth_report(report_md)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "下载 Markdown",
                export_markdown_bytes(report_md),
                file_name="growth_report.md",
                mime="text/markdown",
            )
        with c2:
            st.download_button(
                "下载 PDF（简易）",
                export_simple_pdf_bytes(report_md),
                file_name="growth_report.pdf",
                mime="application/pdf",
            )
else:
    st.info("请在左侧上传 users / products / orders 三张 CSV，校验通过后点击「开始分析」。")
    st.markdown(
        """
**快速体验：**
```bash
python -m data.generate_sample
```
将 `sample_data/` 下三个 CSV 上传即可。
"""
    )
