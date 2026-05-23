# Ecommerce Analysis

电商销售数据分析项目：指标计算、异动检测、根因分析、DeepSeek 策略与增长报告。

## 环境要求

- Python 3.9+
- 依赖见 `requirements.txt`

## 安装

```bash
cd ecommerce_analysis
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 配置 DeepSeek

创建 `.env` 或在系统环境变量中设置：

```env
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
ANOMALY_THRESHOLD=0.15
```

## 生成示例数据（3 个月）

```bash
python -m data.generate_sample
```

输出目录 `sample_data/`：`users.csv`、`products.csv`、`orders.csv`

## 启动应用

```bash
streamlit run app.py
```

浏览器打开 http://localhost:8501

## 项目结构

```
ecommerce_analysis/
├── app.py                 # Streamlit 主入口
├── config.py              # 全局配置
├── data/                  # 表定义与示例数据
├── analysis/              # 指标、异动、根因
├── report/                # 策略与增长报告
├── ui/                    # 上传与展示
├── utils/                 # 数据处理与 LLM
└── prompts/               # Prompt 模板
```

## 各模块独立运行

```bash
python config.py
python -m data.data_definitions
python -m data.generate_sample
python -m utils.data_processor
python -m analysis.metrics
python -m analysis.anomaly
python -m analysis.root_cause
python -m report.strategy
python -m report.growth_report
```

## 数据要求

- 三张表列名与类型见 `data/data_definitions.py`
- **订单表日期须恰好覆盖 3 个连续自然月**
- 单文件上传上限 200MB

## 功能概览

1. **指标分析**：用户 / 产品 / 渠道 / Cohort，周同比 & 月同比
2. **异动检测**：阈值 15%，连续趋势、2σ 偏离、Cohort 恶化
3. **根因分析**：多维度下钻 + 规则验证 + DeepSeek 推理
4. **策略 & 报告**：DeepSeek 生成，支持 Markdown / 简易 PDF 下载
