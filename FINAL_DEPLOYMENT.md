# Matchmaker Backend - MVP 部署完整指南

## 🎯 项目状态

✅ 后端项目已完全配置，可以直接部署！

---

## 📁 项目结构

```
matchmaker-backend/
├── app/                          # 应用主目录
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── users.py      # 用户相关 API
│   │           └── matches.py    # 匹配相关 API
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # 配置管理
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py        # 数据库连接
│   └── main.py                 # FastAPI 应用入口
├── Dockerfile                      # Docker 部署配置
├── render.yaml                    # Render 自动部署配置
├── requirements.txt                # Python 依赖
├── supabase_init.sql            # 数据库初始化脚本
├── package.json                  # 项目元信息
├── DEPLOYMENT.md                 # 详细部署指南
├── DEPLOYMENT_CHECKLIST.md      # 部署检查清单
└── QUICK_DEPLOY.md              # 快速部署指南
```

---

## 🔧 环境变量（已配置）

以下凭据已配置到 `render.yaml`：

```yaml
DATABASE_URL: postgresql://postgres:L.am19961209..@db.lwormsunwjwlutwqnlnt.supabase.co:5432/postgres
SECRET_KEY: matchmaker-jwt-secret-2024-production
SUPABASE_URL: https://lwormsunwjwlutwqnlnt.supabase.co
SUPABASE_ANON_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx3b3Jtc3V3d2x1dHd3FubG50Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzczNTEwMDQsInV4cCI6MjA1OTY5NzQwNH0.UEfFt0zoSlJ3Jm2GzDT6T-R10ZRMLaqypaDWFnwZPjU
```

---

## 🚀 一键部署到 Render

### 步骤 1：初始化 Git 仓库

```bash
cd /data/workspace/matchmaker-backend
git init
git add .
git commit -m "Initial MVP backend - FastAPI + Supabase"
git branch -M main
```

### 步骤 2：创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名称：`matchmaker-backend`
3. 选择 Public/Private
4. 不要初始化 README 或 .gitignore

### 步骤 3：推送代码

```bash
# 替换为你的 GitHub 用户名
git remote add origin https://github.com/<your-username>/matchmaker-backend.git
git push -u origin main
```

### 步骤 4：部署到 Render

#### 方式 A：网页部署（推荐）

1. 访问 https://dashboard.render.com/
2. 用 GitHub 账号登录
3. 点击 "New +"
4. 选择 "Web Service"
5. 点击 "Connect a repository"
6. 选择 `matchmaker-backend` 仓库
7. 配置如下：
   - **Name**: `matchmaker-api`
   - **Region**: `Singapore`
   - **Branch**: `main`
   - **Root Directory**: `.`
   - **Runtime**: `Docker`
   - **Plan**: `Free`
8. 点击 "Create Web Service"

Render 会自动：
- 构建镜像
- 启动容器
- 配置环境变量（从 render.yaml 读取）
- 提供访问 URL

#### 方式 B：命令行部署（可选）

```bash
# 安装 Render CLI
curl -fsSL https://raw.githubusercontent.com/render-oss/render-cli/main/install.sh | bash

# 登录
render login

# 部署
cd /data/workspace/matchmaker-backend
render deploy --service matchmaker-api
```

---

## 📊 部署成功后

### 1. 获取后端 URL

部署完成后，Render 会提供类似：
```
https://matchmaker-api.onrender.com
```

### 2. 验证健康检查

```bash
curl https://matchmaker-api.onrender.com/health
```

预期响应：
```json
{
  "status": "healthy",
  "service": "Matchmaker Backend",
  "environment": "production"
}
```

### 3. 访问 API 文档

在浏览器中打开：
```
https://matchmaker-api.onrender.com/docs
```

### 4. 测试 API 端点

```bash
# 注册用户
curl -X POST https://matchmaker-api.onrender.com/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138000",
    "nickname": "测试用户",
    "gender": 1,
    "birthday": "1995-01-01"
  }'

# 获取推荐
curl -X POST https://matchmaker-api.onrender.com/api/v1/matches/find \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "limit": 10
  }'
```

---

## 🔐 Supabase 数据库配置

### 1. 初始化数据库

1. 访问 https://supabase.com/dashboard
2. 选择你的项目
3. 点击左侧 "SQL Editor"
4. 复制 `supabase_init.sql` 的全部内容
5. 点击 "Run" 执行 SQL

### 2. 验证表创建

在 SQL Editor 运行：
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

应该看到：
- users
- user_profiles
- user_preferences
- matches
- chats
- messages

---

## 🐛 故障排除

### 构建失败

**问题**: Dockerfile 找不到
**解决**: 确保 Dockerfile 在项目根目录

### 数据库连接失败

**问题**: 连接 Supabase 超时
**解决**:
1. 检查 `DATABASE_URL` 格式
2. 确认 Supabase 项目已启动
3. 查看 Render 日志

### 健康检查失败

**问题**: 404 错误
**解决**:
1. 检查 Dockerfile 的 CMD 命令
2. 确认端口配置正确（8000）
3. 查看 Render 日志

### 查看 Render 日志

在 Render Dashboard → 选择你的服务 → Logs 中查看：
- 构建日志
- 运行日志
- 错误信息

---

## 📈 下一步功能开发

部署成功后，建议按优先级开发：

### 第一周（MVP 核心功能）
- [ ] 用户注册/登录（手机号验证码）
- [ ] 完善个人资料
- [ ] 基础推荐算法（简单条件匹配）
- [ ] 双向喜欢匹配
- [ ] 实时聊天（WebSocket）

### 第二周（增强功能）
- [ ] 实名认证（身份证 + 人脸识别）
- [ ] 照片上传（Supabase Storage）
- [ ] 用户搜索（多条件筛选）
- [ ] 消息推送（Firebase/极光）

### 第三周（运营功能）
- [ ] 管理后台（Vue Admin）
- [ ] 会员体系（付费功能）
- [ ] 数据统计 dashboard
- [ ] 举报/封号系统

---

## 🔐 安全建议

⚠️ **重要**：你之前发送的凭据需要立即更新

1. **撤销 Supabase API Key**
   - 访问 Supabase Dashboard
   - Settings → API
   - 重新生成 API Key

2. **更新环境变量**
   - 在 Render Dashboard 更新新的 API Key
   - 更新本地的 render.yaml

3. **使用 GitHub Secrets**（如果使用 Actions 自动部署）
   - 不要在代码中硬编码凭据
   - 使用环境变量或 Secrets

---

## 📊 成本总结

| 平台 | 费用 |
|------|--------|
| Render (免费) | $0/月 |
| Supabase (免费) | $0/月 |
| GitHub (免费) | $0/月 |
| **总计** | **$0/月** |

---

需要我帮你：
- **初始化 Git 仓库**？
- **生成 GitHub Personal Access Token**？
- **创建前端项目**（Vue + Vercel）？
- **测试数据库连接**？
