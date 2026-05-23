"""中英文界面文案"""
from __future__ import annotations

from typing import Any

import pandas as pd

LANG_ZH = "zh"
LANG_EN = "en"
SUPPORTED_LANGS = (LANG_ZH, LANG_EN)

# ---------------------------------------------------------------------------
# Translation tables
# ---------------------------------------------------------------------------

TEXT: dict[str, dict[str, str]] = {
  "app.title": {"zh": "📈 电商销售数据分析", "en": "📈 Ecommerce Sales Analytics"},
  "app.caption": {
    "zh": "指标监控 · 异动检测 · 根因分析 · 策略与增长报告",
    "en": "Metrics · Anomaly Detection · Root Cause · Strategy & Growth Report",
  },
  "app.page_title": {"zh": "电商数据分析", "en": "Ecommerce Analysis"},
  "settings.language": {"zh": "🌐 语言 / Language", "en": "🌐 Language / 语言"},
  "settings.lang_zh": {"zh": "中文", "en": "中文 Chinese"},
  "settings.lang_en": {"zh": "English", "en": "English"},
  "settings.rerun_hint": {
    "zh": "语言已切换，请重新点击「开始分析」以更新结果。",
    "en": "Language changed. Click **Run Analysis** again to refresh results.",
  },
  "upload.header": {"zh": "📁 数据上传", "en": "📁 Data Upload"},
  "upload.caption": {
    "zh": "单文件上限 {max_mb}MB，订单须覆盖连续 3 个月",
    "en": "Max {max_mb}MB per file. Orders must span 3 consecutive calendar months.",
  },
  "upload.download_templates": {"zh": "下载模板", "en": "Download Templates"},
  "upload.users": {"zh": "用户", "en": "Users"},
  "upload.products": {"zh": "产品", "en": "Products"},
  "upload.orders": {"zh": "订单", "en": "Orders"},
  "upload.instructions": {"zh": "📖 上传说明", "en": "📖 Upload Guide"},
  "upload.users_table": {"zh": "### 用户表 users.csv", "en": "### Users — users.csv"},
  "upload.products_table": {"zh": "### 产品表 products.csv", "en": "### Products — products.csv"},
  "upload.orders_table": {"zh": "### 订单表 orders.csv", "en": "### Orders — orders.csv"},
  "upload.file_too_large": {"zh": "{name} 超过 {max_mb}MB", "en": "{name} exceeds {max_mb}MB"},
  "upload.validation_ok": {"zh": "✅ 校验通过", "en": "✅ Validation passed"},
  "btn.run_analysis": {"zh": "🚀 开始分析", "en": "🚀 Run Analysis"},
  "spinner.analyzing": {"zh": "正在计算指标与分析…", "en": "Computing metrics and running analysis…"},
  "spinner.strategy": {"zh": "生成运营策略…", "en": "Generating strategy recommendations…"},
  "spinner.report": {"zh": "生成增长报告…", "en": "Generating growth report…"},
  "tab.metrics": {"zh": "📊 指标变化", "en": "📊 Metrics"},
  "tab.anomaly": {"zh": "⚠️ 异动与趋势", "en": "⚠️ Anomalies & Trends"},
  "tab.root_cause": {"zh": "🔍 根因分析", "en": "🔍 Root Cause"},
  "tab.strategy": {"zh": "💡 策略建议", "en": "💡 Strategy"},
  "tab.report": {"zh": "📄 增长报告", "en": "📄 Growth Report"},
  "tab.users": {"zh": "👤 用户", "en": "👤 Users"},
  "tab.products": {"zh": "📦 产品", "en": "📦 Products"},
  "tab.channels": {"zh": "📣 渠道", "en": "📣 Channels"},
  "tab.cohort": {"zh": "📊 Cohort", "en": "📊 Cohort"},
  "metrics.user_title": {"zh": "用户分层指标", "en": "User Segment Metrics"},
  "metrics.user_help": {
    "zh": "按 cluster 拆分，每张表一个指标，含当月/上月或当周/上周对比",
    "en": "Split by cluster; one table per metric with WoW or MoM comparison",
  },
  "metrics.product_title": {"zh": "品类指标", "en": "Category Metrics"},
  "metrics.product_help": {
    "zh": "按 category 拆分，每张表一个指标",
    "en": "Split by category; one table per metric",
  },
  "metrics.channel_title": {"zh": "渠道指标", "en": "Channel Metrics"},
  "metrics.cohort_title": {"zh": "Cohort 批次分析", "en": "Cohort Analysis"},
  "metrics.cohort_help": {
    "zh": "M1-M3 留存、累计 LTV、AOV、折扣依赖、退货、评分",
    "en": "M1–M3 retention, cumulative LTV, AOV, discount, returns, ratings",
  },
  "metrics.cohort_chart": {"zh": "Cohort 留存曲线", "en": "Cohort Retention Curve"},
  "metrics.cohort_empty": {"zh": "Cohort 数据不足", "en": "Insufficient cohort data"},
  "metrics.insufficient": {"zh": "{prefix}：数据不足，无法计算", "en": "{prefix}: insufficient data"},
  "metrics.week_section": {
    "zh": "**{prefix} · 周对比（最近完整周 vs 上周）**",
    "en": "**{prefix} · WoW (latest full week vs prior week)**",
  },
  "metrics.month_section": {
    "zh": "**{prefix} · 月对比（最近完整月 vs 上月）**",
    "en": "**{prefix} · MoM (latest full month vs prior month)**",
  },
  "metrics.user_level": {"zh": "用户层面", "en": "User Level"},
  "metrics.product_level": {"zh": "品类层面", "en": "Category Level"},
  "metrics.channel_level": {"zh": "渠道层面", "en": "Channel Level"},
  "period.week": {"zh": "周对比", "en": "WoW"},
  "period.month": {"zh": "月对比", "en": "MoM"},
  "anomaly.title": {"zh": "异动检测", "en": "Anomaly Detection"},
  "anomaly.help": {
    "zh": "整体汇总层指标变化超过 15%（每个指标仅一条，避免重复）",
    "en": "Aggregate metrics with >15% change (one line per metric, no duplicates)",
  },
  "anomaly.week_title": {
    "zh": "**本周异动（最近完整周 vs 上周）**",
    "en": "**This Week (latest full week vs prior week)**",
  },
  "anomaly.month_title": {
    "zh": "**本月异动（最近完整月 vs 上月）**",
    "en": "**This Month (latest full month vs prior month)**",
  },
  "anomaly.none": {"zh": "- 暂无", "en": "- None"},
  "anomaly.trends_title": {"zh": "趋势监控", "en": "Trend Monitoring"},
  "anomaly.no_trend": {"zh": "暂无显著趋势", "en": "No significant trends"},
  "root.period_caption": {
    "zh": "下钻对比周期：{prev} → {cur}（订单金额 total_amount 汇总，作为利润/业绩代理指标）",
    "en": "Drill-down period: {prev} → {cur} (total_amount as revenue / profit proxy)",
  },
  "root.drill_title": {"zh": "维度下钻", "en": "Dimension Drill-down"},
  "root.drill_help": {
    "zh": "各维度本月 vs 上月业绩变化，按变化幅度排序",
    "en": "MoM performance change by dimension, sorted by magnitude",
  },
  "root.expander": {"zh": "{dim} · 本月 vs 上月业绩", "en": "{dim} · This Month vs Last Month"},
  "root.attribution": {"zh": "归因链条", "en": "Attribution Chain"},
  "root.ai_analysis": {"zh": "AI 根因推理", "en": "AI Root Cause Analysis"},
  "strategy.title": {"zh": "运营策略建议", "en": "Strategy Recommendations"},
  "report.title": {"zh": "增长报告", "en": "Growth Report"},
  "report.download_md": {"zh": "下载 Markdown", "en": "Download Markdown"},
  "report.download_pdf": {"zh": "下载 PDF（简易）", "en": "Download PDF (simple)"},
  "report.title_md": {"zh": "电商增长分析报告", "en": "Ecommerce Growth Analysis Report"},
  "report.no_api": {
    "zh": "（未配置 DEEPSEEK_API_KEY，跳过 LLM 策略生成）",
    "en": "(DEEPSEEK_API_KEY not set — LLM strategy skipped)",
  },
  "report.no_api_summary": {
    "zh": "## 核心摘要\n请配置 DEEPSEEK_API_KEY 以生成完整 AI 报告。",
    "en": "## Executive Summary\nSet DEEPSEEK_API_KEY to generate the full AI report.",
  },
  "report.strategy_failed": {"zh": "策略生成失败: {err}", "en": "Strategy generation failed: {err}"},
  "report.report_failed": {"zh": "报告生成失败: {err}", "en": "Report generation failed: {err}"},
  "empty.upload_hint": {
    "zh": "请在左侧上传 users / products / orders 三张 CSV，校验通过后点击「开始分析」。",
    "en": "Upload users, products, and orders CSV files in the sidebar, then click **Run Analysis**.",
  },
  "empty.quick_start": {"zh": "**快速体验：**", "en": "**Quick start:**"},
  "empty.sample_hint": {
    "zh": "将 `sample_data/` 下三个 CSV 上传即可。",
    "en": "Upload the three CSV files from `sample_data/`.",
  },
  "col.current": {"zh": "（当期）", "en": " (Current)"},
  "col.previous": {"zh": "（上期）", "en": " (Previous)"},
  "col.change_pct": {"zh": "变化率", "en": "Change %"},
  "col.cluster": {"zh": "用户分层", "en": "Cluster"},
  "col.category": {"zh": "品类", "en": "Category"},
  "col.acquisition_channel": {"zh": "获客渠道", "en": "Acquisition Channel"},
  "col.revenue_cur": {"zh": "当期营收", "en": "Revenue (Current)"},
  "col.revenue_prev": {"zh": "上期营收", "en": "Revenue (Previous)"},
  "col.revenue_change": {"zh": "营收变化额", "en": "Revenue Change"},
  "col.revenue_change_pct": {"zh": "营收变化率", "en": "Revenue Change %"},
  "col.current_month": {"zh": "当期月份", "en": "Current Month"},
  "col.prev_month": {"zh": "上期月份", "en": "Previous Month"},
  "col.cohort_week": {"zh": "Cohort 周", "en": "Cohort Week"},
  "col.cohort_size": {"zh": "Cohort 规模", "en": "Cohort Size"},
  "col.cumulative_ltv": {"zh": "累计 LTV", "en": "Cumulative LTV"},
  "col.aov": {"zh": "客单价", "en": "AOV"},
  "col.avg_discount": {"zh": "平均折扣", "en": "Avg Discount"},
  "col.return_rate": {"zh": "退货率", "en": "Return Rate"},
  "col.avg_rating": {"zh": "平均评分", "en": "Avg Rating"},
  "trend.consecutive": {
    "zh": "连续趋势：周营收第 {start}-{end} 周同向变化",
    "en": "Consecutive trend: weekly revenue moved in the same direction in weeks {start}–{end}",
  },
  "trend.sigma": {
    "zh": "历史对比：最近一周营收 {value:.0f} 偏离3月均值的2σ以上",
    "en": "Historical: latest week revenue {value:.0f} exceeds 2σ from 3-month mean",
  },
  "trend.cohort_decline": {
    "zh": "Cohort 逐批恶化：最近3批 M1 留存连续下降",
    "en": "Cohort decline: M1 retention fell for the last 3 cohorts",
  },
  "chart.weekly_revenue": {"zh": "周营收", "en": "Weekly Revenue"},
  "chart.weekly_revenue_title": {"zh": "周营收趋势", "en": "Weekly Revenue Trend"},
  "chart.m1_retention": {"zh": "M1留存", "en": "M1 Retention"},
  "chart.m1_retention_title": {"zh": "Cohort M1 留存趋势", "en": "Cohort M1 Retention Trend"},
  "cac.assumption": {
    "zh": "CAC 估算假设：CAC = 该渠道新客首单 AOV × 0.35（行业常见获客成本约为首单 GMV 的 35%）。实际投放成本未提供，结果仅供相对比较。",
    "en": "CAC estimate: CAC = first-order AOV × 0.35 (typical acquisition cost ~35% of first-order GMV). Actual ad spend not provided; for relative comparison only.",
  },
  "llm.root_cause_user": {
    "zh": "请基于本月vs上月各维度营收下钻结果，输出根因分析结论与验证链条。",
    "en": "Based on MoM revenue drill-down by dimension, provide root-cause conclusions and validation chains.",
  },
  "llm.strategy_user": {
    "zh": "请基于根因分析，输出短期止损、中期优化、实验方案三类运营建议。",
    "en": "Based on root-cause analysis, provide short-term fixes, mid-term optimizations, and experiment plans.",
  },
  "llm.report_user": {
    "zh": "请生成完整增长报告，包含：核心摘要、问题陈述、根因分析、策略建议、下周关注指标。",
    "en": "Generate a full growth report: executive summary, problem statement, root cause, strategy, and next-week KPIs.",
  },
  "llm.not_called": {"zh": "（LLM 未调用: {err}）", "en": "(LLM not called: {err})"},
  "llm.no_api_key": {"zh": "未设置 DEEPSEEK_API_KEY 环境变量", "en": "DEEPSEEK_API_KEY environment variable is not set"},
  "llm.call_failed": {"zh": "DeepSeek 调用失败: {err}", "en": "DeepSeek API call failed: {err}"},
  "attr.compare_period": {"zh": "对比周期：{prev} → {cur}（营收维度）", "en": "Compare period: {prev} → {cur} (revenue)"},
  "attr.dim_line": {
    "zh": "{dim}维度 [{val}]：营收 {prev:.2f} → {cur:.2f} ({pct:+.1%})，变化额 {change:.2f}",
    "en": "{dim} [{val}]: revenue {prev:.2f} → {cur:.2f} ({pct:+.1%}), change {change:.2f}",
  },
  "attr.discount_up": {
    "zh": "验证：最近月平均折扣率上升，可能与营收/毛利波动相关。",
    "en": "Check: average discount rate rose in the latest month — may affect revenue/margin.",
  },
  "attr.return_up": {
    "zh": "验证：最近月退货率上升，需排查产品质量或预期管理。",
    "en": "Check: return rate rose in the latest month — review product quality or expectations.",
  },
  "val.missing_cols": {"zh": "{name} 缺少列: {cols}", "en": "{name} missing columns: {cols}"},
  "val.extra_cols": {"zh": "{name} 多余列: {cols}", "en": "{name} extra columns: {cols}"},
  "val.orders_empty": {"zh": "订单表为空", "en": "Orders table is empty"},
  "val.month_span": {
    "zh": "订单日期须恰好覆盖 {required} 个连续自然月，当前检测到 {found} 个月: {months}",
    "en": "Orders must span exactly {required} consecutive calendar months; found {found}: {months}",
  },
  "val.month_gap": {"zh": "月份不连续: {months}", "en": "Months are not consecutive: {months}"},
  "val.span_ok": {
    "zh": "日期范围校验通过，覆盖 {span}",
    "en": "Date range OK, spanning {span}",
  },
  "val.orphan_users": {
    "zh": "订单中有 {count} 个 customer_id 不在用户表",
    "en": "{count} customer_id(s) in orders not found in users table",
  },
  "val.churned": {"zh": "users.churned 必须为 0 或 1", "en": "users.churned must be 0 or 1"},
}

USER_METRICS: dict[str, dict[str, str]] = {
  "share": {"zh": "用户占比", "en": "User Share"},
  "active_users": {"zh": "活跃用户数", "en": "Active Users"},
  "avg_discount": {"zh": "平均折扣率", "en": "Avg Discount Rate"},
  "avg_rating": {"zh": "平均评分", "en": "Avg Rating"},
  "return_rate": {"zh": "退货率", "en": "Return Rate"},
  "churn_risk": {"zh": "流失风险", "en": "Churn Risk"},
}

PRODUCT_METRICS: dict[str, dict[str, str]] = {
  "revenue": {"zh": "品类营收", "en": "Category Revenue"},
  "orders": {"zh": "品类销量", "en": "Category Orders"},
  "aov": {"zh": "客单价", "en": "AOV"},
  "return_rate": {"zh": "退货率", "en": "Return Rate"},
  "avg_rating": {"zh": "平均评分", "en": "Avg Rating"},
  "avg_discount": {"zh": "平均折扣率", "en": "Avg Discount Rate"},
}

CHANNEL_METRICS: dict[str, dict[str, str]] = {
  "new_users": {"zh": "新用户数", "en": "New Users"},
  "first_order_aov": {"zh": "首单AOV", "en": "First-Order AOV"},
  "repurchase_rate": {"zh": "复购率", "en": "Repurchase Rate"},
  "ltv": {"zh": "LTV", "en": "LTV"},
  "cac_estimated": {"zh": "CAC估算", "en": "Est. CAC"},
  "roi_ltv_cac": {"zh": "ROI(LTV/CAC)", "en": "ROI (LTV/CAC)"},
  "churn_rate": {"zh": "流失率", "en": "Churn Rate"},
  "avg_rating": {"zh": "平均评分", "en": "Avg Rating"},
  "retention_7d": {"zh": "7日留存率", "en": "7-Day Retention"},
  "retention_30d": {"zh": "30日留存率", "en": "30-Day Retention"},
}

SCOPE_LABELS: dict[str, dict[str, str]] = {
  "user": {"zh": "用户", "en": "User"},
  "product": {"zh": "产品", "en": "Product"},
  "channel": {"zh": "渠道", "en": "Channel"},
}

DIM_LABELS: dict[str, dict[str, str]] = {
  "cluster": {"zh": "用户分层", "en": "User Segment"},
  "channel": {"zh": "获客渠道", "en": "Acquisition Channel"},
  "country": {"zh": "国家", "en": "Country"},
  "category": {"zh": "品类", "en": "Category"},
  "product": {"zh": "产品", "en": "Product"},
}

ATTR_DIM_LABELS: dict[str, dict[str, str]] = {
  "channel": {"zh": "渠道", "en": "Channel"},
  "category": {"zh": "品类", "en": "Category"},
  "cluster": {"zh": "用户分层", "en": "User Segment"},
  "country": {"zh": "国家", "en": "Country"},
}

USER_COLUMN_DOCS: dict[str, str] = {
  "zh": """
| 列名 | 类型 | 说明 |
|------|------|------|
| customer_id | str | 用户唯一 ID |
| country | str | 国家/地区 |
| age | int | 年龄 |
| gender | str | 性别 |
| days_since_last_purchase | int | 距上次购买天数 |
| AOV | float | 历史平均客单价 |
| total_spend | float | 累计消费 |
| total_order | int | 累计订单数 |
| acquisition_channel | str | 获客渠道 |
| avg_review_score | float | 平均评分 |
| return_rate | float | 退货率 |
| churned | int | 是否流失 0/1 |
| cluster | str | 用户分层标签 |
""",
  "en": """
| Column | Type | Description |
|--------|------|-------------|
| customer_id | str | Unique user ID |
| country | str | Country / region |
| age | int | Age |
| gender | str | Gender |
| days_since_last_purchase | int | Days since last purchase |
| AOV | float | Historical average order value |
| total_spend | float | Lifetime spend |
| total_order | int | Lifetime order count |
| acquisition_channel | str | Acquisition channel |
| avg_review_score | float | Average review score |
| return_rate | float | Return rate |
| churned | int | Churned flag 0/1 |
| cluster | str | User segment label |
""",
}

PRODUCT_COLUMN_DOCS: dict[str, str] = {
  "zh": """
| 列名 | 类型 | 说明 |
|------|------|------|
| category | str | 品类 |
| product_name | str | 产品名称 |
| total_orders | int | 累计销量 |
| total_revenue | float | 累计营收 |
| avg_price | float | 平均售价 |
| avg_discount_rate | float | 平均折扣率 |
| return_rate | float | 退货率 |
| avg_rating | float | 平均评分 |
""",
  "en": """
| Column | Type | Description |
|--------|------|-------------|
| category | str | Category |
| product_name | str | Product name |
| total_orders | int | Total orders |
| total_revenue | float | Total revenue |
| avg_price | float | Average price |
| avg_discount_rate | float | Average discount rate |
| return_rate | float | Return rate |
| avg_rating | float | Average rating |
""",
}

ORDER_COLUMN_DOCS: dict[str, str] = {
  "zh": """
| 列名 | 类型 | 说明 |
|------|------|------|
| order_id | str | 订单 ID |
| customer_id | str | 用户 ID |
| order_date | str | 下单日期 YYYY-MM-DD |
| category | str | 品类 |
| product_name | str | 产品名称 |
| discount_rate | float | 折扣率 0-1 |
| total_amount | float | 订单金额 |
| customer_rating | float | 评分 |
| returned | int | 是否退货 0/1 |
""",
  "en": """
| Column | Type | Description |
|--------|------|-------------|
| order_id | str | Order ID |
| customer_id | str | User ID |
| order_date | str | Order date YYYY-MM-DD |
| category | str | Category |
| product_name | str | Product name |
| discount_rate | float | Discount rate 0–1 |
| total_amount | float | Order amount |
| customer_rating | float | Rating |
| returned | int | Returned flag 0/1 |
""",
}


def t(key: str, lang: str = LANG_ZH, **kwargs: Any) -> str:
  lang = lang if lang in SUPPORTED_LANGS else LANG_ZH
  template = TEXT.get(key, {}).get(lang, key)
  if kwargs:
    return template.format(**kwargs)
  return template


def metric_labels(scope: str, lang: str = LANG_ZH) -> dict[str, str]:
  mapping = {"user": USER_METRICS, "product": PRODUCT_METRICS, "channel": CHANNEL_METRICS}
  src = mapping.get(scope, {})
  return {k: v.get(lang, k) for k, v in src.items()}


def all_metric_labels(lang: str = LANG_ZH) -> dict[str, str]:
  out: dict[str, str] = {}
  for scope in ("user", "product", "channel"):
    out.update(metric_labels(scope, lang))
  return out


def scope_label(scope: str, lang: str = LANG_ZH) -> str:
  return SCOPE_LABELS.get(scope, {}).get(lang, scope)


def dim_label(dim: str, lang: str = LANG_ZH) -> str:
  return DIM_LABELS.get(dim, {}).get(lang, dim)


def column_docs(lang: str = LANG_ZH) -> tuple[str, str, str]:
  return USER_COLUMN_DOCS[lang], PRODUCT_COLUMN_DOCS[lang], ORDER_COLUMN_DOCS[lang]


def localize_compare_table(df: pd.DataFrame, dimension_col: str, metric: str, lang: str = LANG_ZH) -> pd.DataFrame:
  """Rename compare-table columns for display."""
  labels = all_metric_labels(lang)
  dim_names = {
    "cluster": t("col.cluster", lang),
    "category": t("col.category", lang),
    "acquisition_channel": t("col.acquisition_channel", lang),
  }
  metric_label = labels.get(metric, metric)
  rename: dict[str, str] = {}
  if dimension_col in df.columns:
    rename[dimension_col] = dim_names.get(dimension_col, dimension_col)
  for suffix, suffix_key in (("_cur", "col.current"), ("_prev", "col.previous"), ("_change_pct", "col.change_pct")):
    col = f"{metric}{suffix}"
    if col in df.columns:
      if suffix == "_change_pct":
        rename[col] = f"{metric_label} {t(suffix_key, lang)}"
      else:
        rename[col] = f"{metric_label}{t(suffix_key, lang)}"
  return df.rename(columns=rename)


def localize_drill_table(df: pd.DataFrame, lang: str = LANG_ZH) -> pd.DataFrame:
  mapping = {
    "cluster": t("col.cluster", lang),
    "category": t("col.category", lang),
    "acquisition_channel": t("col.acquisition_channel", lang),
    "country": dim_label("country", lang),
    "product_name": dim_label("product", lang),
    "revenue_cur": t("col.revenue_cur", lang),
    "revenue_prev": t("col.revenue_prev", lang),
    "revenue_change": t("col.revenue_change", lang),
    "revenue_change_pct": t("col.revenue_change_pct", lang),
    "current_month": t("col.current_month", lang),
    "prev_month": t("col.prev_month", lang),
  }
  return df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})


def localize_cohort_table(df: pd.DataFrame, lang: str = LANG_ZH) -> pd.DataFrame:
  mapping = {
    "cohort_week": t("col.cohort_week", lang),
    "cohort_size": t("col.cohort_size", lang),
    "M1_retention": "M1 Retention" if lang == LANG_EN else "M1 留存",
    "M2_retention": "M2 Retention" if lang == LANG_EN else "M2 留存",
    "M3_retention": "M3 Retention" if lang == LANG_EN else "M3 留存",
    "cumulative_ltv": t("col.cumulative_ltv", lang),
    "aov": t("col.aov", lang),
    "avg_discount": t("col.avg_discount", lang),
    "return_rate": t("col.return_rate", lang),
    "avg_rating": t("col.avg_rating", lang),
  }
  return df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})


def render_language_selector() -> str:
  """Sidebar language selector; returns current lang code."""
  import streamlit as st

  options = {LANG_ZH: t("settings.lang_zh", LANG_ZH), LANG_EN: t("settings.lang_en", LANG_EN)}
  if "lang" not in st.session_state:
    st.session_state.lang = LANG_ZH

  selected = st.sidebar.selectbox(
    t("settings.language", st.session_state.lang),
    options=list(options.keys()),
    format_func=lambda k: options[k],
    key="lang_selector",
  )
  if selected != st.session_state.lang:
    st.session_state.lang = selected
    if st.session_state.get("analysis_done") and st.session_state.get("analysis_lang") != selected:
      st.sidebar.warning(t("settings.rerun_hint", selected))
  return st.session_state.lang
