# 一步一步搭建 Agent

这是一个最小可用的 **AI Agent** 示例：能根据用户问题自动决定是否调用工具（查天气、计算、检索），并循环直到给出最终回答。

---

## 第一步：准备环境

### 1.1 安装 Python

- 确保本机已安装 **Python 3.10+**。
- 在终端执行：`python --version` 或 `python3 --version` 检查。

### 1.2 创建虚拟环境（推荐）

在项目根目录 `Agent` 下执行：

```bash
python -m venv venv
```

- Windows 激活：`venv\Scripts\activate`
- macOS/Linux：`source venv/bin/activate`

### 1.3 安装依赖

```bash
pip install -r requirements.txt
```

依赖包括：`openai`（调用大模型）、`python-dotenv`（从 `.env` 读配置）。

---

## 第二步：配置 API Key

1. 复制示例配置：
   - 将 `.env.example` 复制为 `.env`
2. 编辑 `.env`，填入你的 OpenAI API Key：
   ```env
   OPENAI_API_KEY=sk-your-api-key-here
   ```
3. 若使用国内或其它兼容 OpenAI 的接口，可在 `config.py` 中增加 `base_url` 等配置，并在 `agent.py` 里创建 `OpenAI(...)` 时传入。

---

## 第三步：理解项目结构

```
Agent/
├── .env              # 你的配置（不要提交到 Git）
├── .env.example      # 配置示例
├── config.py         # 读取环境变量
├── tools.py          # 工具定义（名字、描述、参数、实现）
├── agent.py          # Agent 核心：对话 + 工具调用循环
├── main.py           # 主入口：终端对话
├── requirements.txt
└── README.md
```

- **tools.py**：定义 Agent 能用的“工具”（函数 + 给模型的说明）。可在这里新增工具。
- **agent.py**：负责把用户消息发给 LLM，若 LLM 返回“要调用工具”，就执行对应函数并把结果再发给 LLM，直到 LLM 不再调工具并给出文本回复。

---

## 第四步：运行 Agent

在项目根目录、已激活虚拟环境的情况下执行：

```bash
python main.py
```

然后输入问题，例如：

- “北京今天天气怎么样？” → 会调用 `get_weather`
- “计算 (1+2)*3” → 会调用 `calculator`
- “你好” → 可能直接回复，不调工具

输入 `quit` 或 `exit` 退出。

---

## 第五步：扩展你的 Agent

1. **增加新工具**
   - 在 `tools.py` 里写一个新函数（如 `send_email`）。
   - 在 `TOOLS` 里增加一项（name、description、parameters）。
   - 在 `TOOL_FUNCTIONS` 里把名字映射到该函数。

2. **改模型或接口**
   - 在 `agent.py` 的 `client.chat.completions.create` 里修改 `model`。
   - 若用其它兼容 OpenAI 的 API，在 `config.py` 和创建 `OpenAI(...)` 时设置 `base_url`、`api_key` 等。

3. **改成 API 服务**
   - 用 FastFlask/Flask 等包，在路由里调用 `run_agent(request.json["message"])` 并返回结果即可。

---

## 常见问题

- **报错缺少 OPENAI_API_KEY**  
  检查是否已创建 `.env` 并写入了 `OPENAI_API_KEY=sk-...`。

- **想用国产大模型**  
  若该模型提供兼容 OpenAI 的 API，只需在代码里改 `base_url` 和 `api_key`，工具调用格式一般可复用。

按以上步骤即可完成从零到可运行 Agent 的搭建；后续只需在 `tools.py` 和 `agent.py` 上继续扩展。
