"""
工具定义：Agent 可以调用的函数。
每增加一个工具，就在 TOOLS 列表里加一项，并实现对应函数。
"""

def get_weather(city: str) -> str:
    """查询某城市的天气（示例：模拟返回）。"""
    # 实际项目可接真实天气 API
    return f"[模拟] {city} 当前：晴，25°C"

def calculator(expression: str) -> str:
    """计算数学表达式，例如：1+2*3。只支持 + - * / 和数字。"""
    try:
        # 仅允许数字和四则运算，避免执行任意代码
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            return "错误：只支持数字和 + - * / ( )"
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"

def search_knowledge(query: str) -> str:
    """知识库检索（示例：模拟）。实际可接向量库。"""
    return f"[模拟] 关于「{query}」的检索结果：这是示例回答。"

# 供 OpenAI 使用的工具声明（名字、描述、参数）
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式，如 1+2*3",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "在知识库中检索与问题相关的内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "检索关键词或问题"}
                },
                "required": ["query"]
            }
        }
    }
]

# 名字 -> 实际函数的映射
TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "calculator": calculator,
    "search_knowledge": search_knowledge,
}
