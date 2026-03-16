"""配置：从环境变量读取 API Key 等"""
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("警告：未设置 OPENAI_API_KEY，请在 .env 中配置")
