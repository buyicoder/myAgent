"""配置：从环境变量读取 API Key 等"""
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # 可选，用于兼容 OpenAI 的其它接口
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # 模型名，用国内 API 时需改

# 企查查开放平台（用于融资信息核查等）
QCC_API_KEY = os.getenv("QCC_API_KEY")       # 开放平台 AppKey
QCC_SECRET_KEY = os.getenv("QCC_SECRET_KEY") # 开放平台 SecretKey

# 飞书开放平台（用于把导出的 Excel 上传到云文档）
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")           # 自建应用 App ID（cli_ 开头）
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")   # 自建应用 App Secret
FEISHU_FOLDER_TOKEN = os.getenv("FEISHU_FOLDER_TOKEN")  # 云文档目录的 folder token，文件将上传到此目录

if not OPENAI_API_KEY:
    print("警告：未设置 OPENAI_API_KEY，请在 .env 中配置")
