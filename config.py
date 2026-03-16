"""配置：从环境变量读取 API Key 等"""
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # 可选，用于兼容 OpenAI 的其它接口
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # 模型名，用国内 API 时需改
if not OPENAI_API_KEY:
    print("警告：未设置 OPENAI_API_KEY，请在 .env 中配置")
