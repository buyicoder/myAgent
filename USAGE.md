# Agent 使用说明（一步步来）

## 关于 API Key：能用 Cursor 的 Key 吗？

**不能。** 这个 Agent 调用的是 **OpenAI 官方 API**（或其它兼容 OpenAI 格式的接口），和 Cursor 编辑器用的不是同一套。

- **Cursor 的 API Key**：只在 Cursor 里用，用来让 Cursor 调用 AI，不能填到本项目的 `.env` 里当 `OPENAI_API_KEY` 用。
- **本项目需要的**：到 [OpenAI 平台](https://platform.openai.com/api-keys) 注册/登录，在 **API Keys** 里创建一个 Key（格式一般是 `sk-...`），把这段 Key 填到下面的 `.env` 里。

如果你用的是**国产大模型或其它兼容 OpenAI 的接口**（例如某家提供的「OpenAI 兼容 API」），只要对方给你的是「API Key + 接口地址」，也可以在本项目里用，后面会说明如何配置。

---

## 第一步：打开项目目录

在终端（PowerShell 或 CMD）里执行：

```powershell
cd "c:\Users\18779\Desktop\联盟工作\Agent"
```

---

## 第二步：用 Miniconda 创建并激活环境

```powershell
# 用 environment.yml 创建名为 agent 的环境（含 Python 与依赖）
conda env create -f environment.yml

# 激活环境
conda activate agent
```

激活成功后，命令行前面会出现 `(agent)`。

（若未安装 Miniconda，请先到 [Miniconda 官网](https://docs.conda.io/en/latest/miniconda.html) 下载安装。）

---

## 第三步：若未用 environment.yml，可手动装依赖

若你是用 `conda create -n agent python=3.10` 手动建的环境，再执行：

```powershell
pip install -r requirements.txt
```

---

## 第四步：配置 API Key

1. 在项目根目录找到 **`.env.example`**，复制一份，重命名为 **`.env`**。
2. 用记事本或 Cursor 打开 **`.env`**，把里面的内容改成你的 Key：

```env
OPENAI_API_KEY=sk-你的OpenAI的Key
```

保存后关闭。**不要**把 `.env` 上传到 Git（已在 `.gitignore` 里忽略）。

---

## 第五步：运行 Agent

在**已激活 Conda 环境**（`conda activate agent`）的情况下执行：

```powershell
python main.py
```

看到类似提示说明启动成功：

```
Agent 已启动。输入问题后回车，输入 quit 或 exit 退出。

你:
```

---

## 第六步：和 Agent 对话

在 **你:** 后面输入问题并回车，例如：

| 你输入 | Agent 会做什么 |
|--------|-----------------|
| 北京今天天气怎么样？ | 调用「查天气」工具后回答 |
| 算一下 (1+2)*3 | 调用「计算器」工具后回答 |
| 你好 | 直接文字回复，不调工具 |
| quit 或 exit | 退出程序 |

回答会出现在 **Agent:** 后面。输入 `quit` 或 `exit` 再回车即可退出。

---

## 使用流程小结

1. `cd` 到项目目录  
2. 激活 Conda 环境：`conda activate agent`  
3. 首次使用：复制 `.env.example` 为 `.env`，填好 `OPENAI_API_KEY`  
4. 运行：`python main.py`  
5. 在「你:」后输入问题，看「Agent:」的回复  

---

## 使用其它兼容 OpenAI 的 API（可选）

如果你用的是**非 OpenAI 官方**、但兼容 OpenAI 格式的接口（例如某些国内 API），需要同时配置「接口地址」和「Key」：

1. 在 **`.env`** 里增加一行（把地址换成对方给的）：

```env
OPENAI_API_KEY=你的Key
OPENAI_BASE_URL=https://对方提供的接口地址/v1
```

2. 项目里要能读取 `OPENAI_BASE_URL` 并传给 `OpenAI(...)`。若当前代码没有，可以让我帮你改一版支持 `OPENAI_BASE_URL` 的配置。

---

总结：**不要用 Cursor 的 API Key**；用 **OpenAI 平台** 的 Key（或其它兼容服务的 Key），按上面步骤配置 `.env` 即可使用本 Agent。
