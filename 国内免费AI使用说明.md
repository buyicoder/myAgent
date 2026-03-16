# 国内免费 AI 与 API 推荐 + 一步步使用说明

## 一、推荐：国内免费 AI 与 API

### 首选：智谱 AI（GLM-4-Flash）

- **平台**：[智谱 AI 开放平台](https://open.bigmodel.cn)
- **免费模型**：**GLM-4-Flash**（首个免费大模型 API，支持 128K 上下文）
- **特点**：接口**完全兼容 OpenAI**，本项目无需改代码，只改配置即可；支持**工具调用（Function Calling）**，和当前 Agent 完美匹配。
- **免费额度**：注册即可用，具体额度以官网为准。

### 备选：阿里云通义千问（DashScope）

- **平台**：[阿里云百炼 / DashScope](https://dashscope.aliyun.com)
- **免费额度**：新用户有大量免费 Token（具体见官网）。
- **特点**：提供 **OpenAI 兼容模式**，同样只需改 `base_url` 和 `api_key`，模型名改为 `qwen-turbo` 或 `qwen-plus` 等。

本说明**以智谱为例**，一步步教你在本项目里用国内免费 API。

---

## 二、用智谱 API 一步步操作

### 第一步：注册并获取 API Key

1. 打开浏览器，访问：**https://open.bigmodel.cn**
2. 点击「注册/登录」，用手机号或第三方账号注册。
3. 登录后进入「**控制台**」或「**API Key 管理**」。
4. 新建或复制一个 **API Key**（形如一长串字母数字），保存到记事本备用。

（若需实名认证，按页面提示完成即可开通 API。）

### 第二步：在项目里配置 .env

1. 打开项目根目录下的 **`.env`** 文件（若没有，从 **`.env.example`** 复制一份并重命名为 `.env`）。
2. 按下面两种方式二选一填写。

**方式 A：只用智谱（推荐）**

在 `.env` 里写成：

```env
OPENAI_API_KEY=你的智谱APIKey
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
OPENAI_MODEL=glm-4-flash
```

把 `你的智谱APIKey` 替换成你在智谱开放平台复制的 Key。

**方式 B：保留 OpenAI，多写几行**

例如保留原来的 OpenAI Key，并增加智谱配置（本项目会优先使用 `OPENAI_BASE_URL`，所以会走智谱）：

```env
OPENAI_API_KEY=你的智谱APIKey
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
OPENAI_MODEL=glm-4-flash
```

3. 保存并关闭 `.env`。

### 第三步：确认环境与依赖（Miniconda）

在项目目录下打开终端，执行：

```powershell
cd "c:\Users\18779\Desktop\联盟工作\Agent"
conda env create -f environment.yml
conda activate agent
```

若已创建过 `agent` 环境，只需执行 `conda activate agent`。确保没有报错。

### 第四步：运行 Agent

在已激活 Conda 环境（`conda activate agent`）的前提下执行：

```powershell
python main.py
```

看到「Agent 已启动。输入问题后回车……」即表示成功。

### 第五步：试用

在 **你:** 后输入问题，例如：

- 「北京今天天气怎么样」
- 「算一下 100 除以 3」
- 「你好」

Agent 会通过**智谱 GLM-4-Flash** 和现有工具（天气、计算器、知识检索）回答你。

---

## 三、可选：改用通义千问（阿里云）

若你选择用**阿里云通义千问**的兼容接口：

1. 在 [阿里云 DashScope](https://dashscope.aliyun.com) 注册并获取 **API Key**。
2. 在 **`.env`** 里配置：

```env
OPENAI_API_KEY=你的阿里云DashScope的Key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-turbo
```

3. 保存后同样执行 `python main.py` 即可。

（若通义某版本对工具调用有差异，以阿里云最新文档为准。）

---

## 四、小结

| 项目     | 说明 |
|----------|------|
| **国内免费 AI** | 推荐 **智谱 GLM-4-Flash**，备选 **阿里通义千问**。 |
| **国内免费 API** | 智谱：`https://open.bigmodel.cn` 获取 Key；阿里：DashScope 兼容模式。 |
| **怎么用** | 在 `.env` 里设置 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`，然后 `python main.py`。 |

按上面步骤即可在本项目中用国内免费 AI 和 API，无需改代码，只改配置。
