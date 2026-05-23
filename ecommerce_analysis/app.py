"""
电商销售数据分析 — Streamlit 主应用
启动: streamlit run app.py
"""
from __future__ import annotations

import os

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
from utils.i18n import render_language_selector, t

load_dotenv()

lang = render_language_selector()

st.set_page_config(
    page_title=t("app.page_title", lang),
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title(t("app.title", lang))
st.caption(t("app.caption", lang))

validated = render_upload_sidebar(lang)

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if validated and st.sidebar.button(t("btn.run_analysis", lang), type="primary", use_container_width=True):
    with st.spinner(t("spinner.analyzing", lang)):
        users = validated["users"]
        products = validated["products"]
        orders = validated["orders"]

        metrics = compute_all_metrics(users, products, orders, lang=lang)
        anomaly = run_anomaly_analysis(metrics, orders, lang=lang)
        root = run_root_cause(
            orders,
            users,
            anomaly,
            use_llm=bool(os.getenv("DEEPSEEK_API_KEY")),
            lang=lang,
        )

        strategy = ""
        report = ""
        if os.getenv("DEEPSEEK_API_KEY"):
            try:
                with st.spinner(t("spinner.strategy", lang)):
                    strategy = generate_strategy(
                        root, metrics_summary=str(metrics.get("metrics_flat", "")), lang=lang
                    )
                with st.spinner(t("spinner.report", lang)):
                    ctx = build_report_context(metrics, anomaly, root, strategy)
                    report = generate_growth_report(ctx, lang=lang)
            except Exception as e:
                strategy = t("report.strategy_failed", lang, err=e)
                report = t("report.report_failed", lang, err=e)
        else:
            strategy = t("report.no_api", lang)
            report = report_to_markdown(
                t("report.no_api_summary", lang) + "\n\n" + "\n".join(anomaly.get("month_anomalies", [])),
                lang=lang,
            )

        st.session_state.update(
            {
                "analysis_done": True,
                "analysis_lang": lang,
                "metrics": metrics,
                "anomaly": anomaly,
                "root": root,
                "strategy": strategy,
                "report_md": report_to_markdown(report if report.startswith("#") else report, lang=lang),
            }
        )

if st.session_state.get("analysis_done"):
    content_lang = st.session_state.get("analysis_lang", lang)
    if content_lang != lang:
        st.warning(t("settings.rerun_hint", lang))

    metrics = st.session_state["metrics"]
    anomaly = st.session_state["anomaly"]
    root = st.session_state["root"]
    strategy = st.session_state["strategy"]
    report_md = st.session_state["report_md"]

    t1, t2, t3, t4, t5 = st.tabs([
        t("tab.metrics", lang),
        t("tab.anomaly", lang),
        t("tab.root_cause", lang),
        t("tab.strategy", lang),
        t("tab.report", lang),
    ])

    with t1:
        show_metrics_tabs(metrics, content_lang)
    with t2:
        show_anomaly_results(anomaly, content_lang)
    with t3:
        show_root_cause(root, content_lang)
    with t4:
        show_strategy(strategy, content_lang)
    with t5:
        show_growth_report(report_md, lang)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                t("report.download_md", lang),
                export_markdown_bytes(report_md),
                file_name="growth_report.md",
                mime="text/markdown",
            )
        with c2:
            st.download_button(
                t("report.download_pdf", lang),
                export_simple_pdf_bytes(report_md),
                file_name="growth_report.pdf",
                mime="application/pdf",
            )
else:
    st.info(t("empty.upload_hint", lang))
    st.markdown(
        f"""
{t("empty.quick_start", lang)}
```bash
python -m data.generate_sample
```
{t("empty.sample_hint", lang)}
"""
    )
