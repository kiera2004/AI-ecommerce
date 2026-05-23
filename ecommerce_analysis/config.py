"""全局配置"""
import os

# 异动阈值（15%），可在 UI 或环境变量中覆盖
ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", "0.15"))

# DeepSeek / OpenAI 兼容 API
LLM_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
LLM_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
LLM_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))

# 上传限制
MAX_UPLOAD_SIZE_MB = 200
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# 订单表必须覆盖的连续月份数
REQUIRED_ORDER_MONTHS = 3

# CAC 估算假设（无实际营销成本时使用）
CAC_ASSUMPTION = (
    "CAC 估算假设：CAC = 该渠道新客首单 AOV × 0.35（行业常见获客成本约为首单 GMV 的 35%）。"
    "实际投放成本未提供，结果仅供相对比较。"
)

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")
