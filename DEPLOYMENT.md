# Matchmaker Backend - MVP 部署指南

## 🚀 免费部署方案

本指南帮助你将相亲网站后端部署到 **完全免费的云端平台**。

---

## 技术栈

| 组件 | 平台 | 费用 |
|------|------|------|
| 后端 | Render | 免费 |
| 数据库 | Supabase | 免费 |
| 前端 | Vercel | 免费 |

---

## 第一步：部署到 Render

### 1. 准备代码

```bash
cd /data/workspace/matchmaker-backend
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo>
git push -u origin main
```

### 2. 连接 GitHub 到 Render

1. 访问 https://dashboard.render.com/
2. 点击 "New +"
3. 选择 "Web Service"
4. 连接 GitHub 仓库
5. Render 自动检测 `render.yaml` 配置

### 3. 配置环境变量

在 Render 控制台设置以下环境变量：

```bash
DATABASE_URL=postgresql://<supabase-user>:<password>@<supabase-host>:5432/postgres
SECRET_KEY=<your-secret-key>
ENVIRONMENT=production
```

### 4. 部署完成

Render 会自动部署，你将获得：
- 后端 URL：`https://matchmaker-backend.onrender.com`
- 自动 HTTPS
- 自动重启

---

## 第二步：配置 Supabase 数据库

### 1. 创建 Supabase 项目

1. 访问 https://supabase.com/
2. 点击 "New Project"
3. 项目名称：`matchmaker-db`
4. 密码：设置数据库密码
5. 区域：选择最近的区域（如 Singapore）

### 2. 运行 SQL 初始化

1. 进入 Supabase Dashboard
2. 点击 "SQL Editor"
3. 运行 `supabase_init.sql` 中的 SQL

### 3. 获取数据库连接信息

在 Supabase Dashboard → Settings → Database 中获取：

```bash
# 复制 Connection String
postgresql://postgres.<project-ref>:<password>@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

### 4. 配置到 Render

将上面的 `DATABASE_URL` 配置到 Render 的环境变量中。

---

## 第三步：部署前端（可选）

### 使用 Vercel 部署

```bash
# 创建前端项目
cd /data/workspace
mkdir matchmaker-frontend
cd matchmaker-frontend

# 使用 Vite + Vue 3
npm create vite@latest matchmaker-frontend -- --template vue
```

1. 访问 https://vercel.com/
2. 导入 GitHub 仓库
3. 自动部署
4. 获得前端 URL：`https://matchmaker-frontend.vercel.app`

---

## 第四步：配置域名（可选）

### 使用 Cloudflare 免费域名

1. 访问 https://dash.cloudflare.com/sign-up
2. 注册免费账户
3. 添加你的域名
4. 配置 DNS：

| 类型 | 名称 | 值 |
|------|------|------|
| CNAME | api | `matchmaker-backend.onrender.com` |
| CNAME | www | `matchmaker-frontend.vercel.app` |

---

## 第五步：验证部署

### 1. 测试后端

```bash
# 测试健康检查
curl https://matchmaker-backend.onrender.com/health

# 测试 API 文档
open https://matchmaker-backend.onrender.com/docs
```

### 2. 测试数据库

```bash
# 在 Supabase SQL Editor 测试查询
SELECT COUNT(*) FROM users;
```

### 3. 测试前端

```bash
# 访问前端
open https://matchmaker-frontend.vercel.app
```

---

## 第六步：配置 GitHub Actions（自动部署）

### 创建 GitHub Actions Workflow

在 `.github/workflows/deploy.yml` 中添加：

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Render
        run: |
          curl -X POST https://api.render.com/v1/services/${{ secrets.RENDER_SERVICE_ID }}/deploy \
            -H "Authorization: Bearer ${{ secrets.RENDER_API_KEY }}"
```

---

## 总费用

| 平台 | 月费用 |
|------|--------|
| Render | $0 |
| Supabase | $0 |
| Vercel | $0 |
| Cloudflare | $0 |
| **总计** | **$0/月** |

---

## 下一步

部署完成后，你可以：

1. ✅ 访问相亲网站前端
2. ✅ 测试用户注册功能
3. ✅ 查看数据库数据
4. ✅ 根据反馈优化功能

需要我帮你：
- 创建前端项目？
- 编写具体的 API 接口？
- 生成数据库初始化脚本？
