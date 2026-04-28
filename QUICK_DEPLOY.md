# Matchmaker Backend - 一键部署指南（配置已添加）

## ✅ 重要提示

⚠️ **凭据已添加到项目配置中！**

**已配置的内容**：
- ✅ Supabase 数据库 URL
- ✅ JWT 密钥
- ✅ CORS 允许域名
- ✅ Supabase 客户端配置

---

## 🚀 直接部署步骤

### 步骤 1：初始化 Git 并推送

```bash
cd /data/workspace/matchmaker-backend

# 初始化 Git
git init
git add .
git commit -m "Initial MVP backend with configured credentials"

# 推送到 GitHub（替换为你的用户名）
git remote add origin https://github.com/<your-username>/matchmaker-backend.git
git branch -M main
git push -u origin main
```

### 步骤 2：部署到 Render

1. 访问 https://dashboard.render.com/
2. 用 GitHub 账号登录
3. 点击 "New +"
4. 选择 "Web Service"
5. 点击 "Connect a repository"
6. 选择 `matchmaker-backend` 仓库
7. 配置如下：

**基本配置**：
- Name: `matchmaker-api`
- Region: `Singapore`
- Branch: `main`
- Runtime: `Docker`
- Root Directory: `.`
- Plan: `Free`

**环境变量**（render.yaml 已自动加载）：
- `DATABASE_URL`: 自动配置 ✅
- `SECRET_KEY`: 自动配置 ✅
- `SUPABASE_URL`: 自动配置 ✅
- `SUPABASE_ANON_KEY`: 自动配置 ✅
- `ENVIRONMENT`: 自动配置 ✅

8. 点击 "Create Web Service"

---

### 步骤 3：等待部署完成

- Render 自动构建 Docker 镜像（约 2-3 分钟）
- 自动启动容器（约 1 分钟）
- 完成后显示：**Service is live**

### 步骤 4：获取后端 URL

部署完成后，Render 会提供：
```
https://matchmaker-api.onrender.com
```

---

### 步骤 5：验证部署

#### 测试健康检查
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

#### 测试 API 文档
在浏览器打开：
```
https://matchmaker-api.onrender.com/docs
```

#### 测试用户注册
```bash
curl -X POST https://matchmaker-api.onrender.com/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138000",
    "nickname": "测试用户",
    "gender": 1,
    "birthday": "1995-01-01"
  }'
```

---

## 📊 Supabase 数据库配置

### 1. 创建项目

1. 访问 https://supabase.com/
2. 点击 "New Project"
3. 配置：
   - Name: `matchmaker`
   - Database Password: `<your-password>`
   - Region: `Southeast Asia (Singapore)`

### 2. 运行初始化 SQL

1. 进入 Supabase Dashboard → SQL Editor
2. 复制 `supabase_init.sql` 的全部内容
3. 点击 "Run" 执行 SQL

### 3. 验证表创建

运行以下 SQL 查询：
```sql
SELECT table_name
FROM information_schema.tables
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

## 🎯 API 端点（可用）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/` | 根路径（返回版本信息） |
| POST | `/api/v1/users/register` | 用户注册 |
| GET | `/api/v1/users/profile/{id}` | 获取用户资料 |
| PUT | `/api/v1/users/profile/{id}` | 更新用户资料 |
| POST | `/api/v1/matches/find` | 查找匹配 |
| POST | `/api/v1/matches/like/{user}/{target}` | 喜欢用户 |

---

## 🐛 调试问题

### 部署失败

**问题**: Docker 构建失败
**解决**:
1. 检查 Dockerfile 是否在根目录
2. 查看 Render Dashboard → Logs → Build logs

### 数据库连接失败

**问题**: 无法连接 Supabase
**解决**:
1. 检查 DATABASE_URL 格式
2. 确认 Supabase 项目已启动
3. 查看 Render 运行日志

### 404 错误

**问题**: API 端点不存在
**解决**:
1. 检查路由前缀配置
2. 查看 `/docs` 中列出的可用端点

### CORS 错误

**问题**: 前端无法访问 API
**解决**:
1. 检查 BACKEND_CORS_ORIGINS 配置
2. 确认前端 URL 已添加到白名单

---

## 📋 部署检查清单

- [ ] Git 仓库已创建
- [ ] 代码已推送到 GitHub main 分支
- [ ] Render Web Service 已创建
- [ ] 部署成功（状态：Live）
- [ ] 健康检查通过
- [ ] API 文档可访问
- [ ] Supabase SQL 已运行
- [ ] 数据库表已验证

---

## 🔐 安全建议

1. **立即撤销当前的 Supabase API Key**（已暴露在聊天记录）
2. 在 Supabase Dashboard 重新生成 API Key
3. 在 Render 更新环境变量
4. 启用 Supabase 项目访问日志
5. 配置数据库备份

---

## 📈 下一步

部署成功后：

1. ✅ 测试所有 API 端点
2. ✅ 验证数据库连接和数据写入
3. ✅ 创建前端项目（Vue + Vercel）
4. ✅ 配置前端连接后端 API
5. ✅ 开发更多功能（认证、匹配算法等）

---

## 💰 费用总结

| 平台 | 费用 |
|------|------|
| Render | $0/月 |
| Supabase | $0/月 |
| GitHub | $0/月 |
| **总计** | **$0/月** |

---

**配置已添加，可以直接部署！** 🚀
