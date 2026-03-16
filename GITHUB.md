# 上传到 GitHub

项目已用 Git 管理，按下面步骤即可推到你的 GitHub。

## 1. 配置 Git 用户信息（若尚未配置）

在任意目录执行一次即可（请改成你的名字和邮箱）：

```bash
git config --global user.name "你的名字或GitHub用户名"
git config --global user.email "你的邮箱@example.com"
```

## 2. 在 GitHub 上新建仓库

1. 打开 https://github.com/new
2. **Repository name** 填：`Agent`（或你喜欢的名字）
3. 选择 **Public**
4. **不要**勾选 "Add a README"（仓库保持空）
5. 点击 **Create repository**

## 3. 在本地添加远程并推送

在项目目录 `Agent` 下执行（把 `你的用户名` 和 `仓库名` 换成你的）：

```bash
cd "c:\Users\18779\Desktop\联盟工作\Agent"

# 添加远程（替换为你的 GitHub 用户名和仓库名）
git remote add origin https://github.com/你的用户名/仓库名.git

# 推送到 GitHub（若仓库默认分支是 main，可改为：git branch -M main && git push -u origin main）
git push -u origin master
```

若 GitHub 提示你新建的是 `main` 分支，可先执行：

```bash
git branch -M main
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main
```

## 4. 使用 SSH（可选）

若已配置 SSH 密钥，可用 SSH 地址替代 HTTPS：

```bash
git remote add origin git@github.com:你的用户名/仓库名.git
git push -u origin main
```

---

推送时若要求登录，请使用 GitHub 用户名 + **Personal Access Token**（在 GitHub → Settings → Developer settings → Personal access tokens 里生成），不要用登录密码。
