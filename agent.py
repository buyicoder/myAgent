"""
Agent 核心：与 LLM 对话，解析工具调用，执行工具并循环直到给出最终回答。
"""
import json
from openai import OpenAI

from config import OPENAI_API_KEY
from tools import TOOLS, TOOL_FUNCTIONS


SYSTEM_PROMPT = """你是一个有帮助的助手。你可以使用以下工具来回答问题：
- get_weather: 查询城市天气
- calculator: 计算数学表达式
- search_knowledge: 检索知识库

若需要用到工具，就按模型要求调用工具；拿到工具结果后再组织成最终回复。若不需要工具，直接回答即可。"""


def run_tool(name: str, arguments: dict) -> str:
    """执行指定工具，返回字符串结果。"""
    if name not in TOOL_FUNCTIONS:
        return f"未知工具: {name}"
    fn = TOOL_FUNCTIONS[name]
    try:
        return fn(**arguments)
    except Exception as e:
        return f"工具执行错误: {e}"


def run_agent(user_message: str, max_rounds: int = 5) -> str:
    """
    运行 Agent：发用户消息给 LLM，若有 tool_calls 就执行工具并把结果送回，循环直到无工具调用或达到最大轮数。
    返回最后一轮助手的文本回复。
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    for _ in range(max_rounds):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        choice = response.choices[0]
        msg = choice.message

        if msg.tool_calls:
            # 把助手消息（含 tool_calls）加入历史
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in msg.tool_calls
                ],
            })
            # 对每个 tool_call 执行并追加 tool 结果
            for tc in msg.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                result = run_tool(name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })
            continue

        # 没有 tool_calls，返回助手文本
        return (msg.content or "").strip()

    return "达到最大轮数，未得到最终回复。"
