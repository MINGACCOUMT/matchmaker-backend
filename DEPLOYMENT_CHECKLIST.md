# Matchmaker Backend - 部署检查清单

## ✅ 部署前准备

- [ ] 准备 GitHub 仓库
- [ ] 推送代码到 GitHub main 分支
- [ ] 注册 Supabase 账户
- [ ] 注册 Render 账户
- [ ] （可选）注册 Vercel 账户
- [ ] （可选）注册 Cloudflare 账户

---

## ✅ 数据库部署

- [ ] 在 Supabase 创建项目 `matchmaker-db`
- [ ] 在 SQL Editor 运行 `supabase_init.sql`
- [ ] 获取 Supabase Connection String
- [ ] 测试数据库连接

---

## ✅ 后端部署

- [ ] 在 Render 导入 GitHub 仓库
- [ ] 配置 Render 环境变量：
  - [ ] `DATABASE_URL` = Supabase Connection String
  - [ ] `SECRET_KEY` = 随机生成的密钥
  - [ ] `ENVIRONMENT` = production
- [ ] 等待 Render 部署完成
- [ ] 测试健康检查：`https://<your-app>.onrender.com/health`
- [ ] 测试 API 文档：`https://<your-app>.onrender.com/docs`

---

## ✅ 前端部署

- [ ] 在 Vercel 导入 GitHub 仓库
- [ ] 配置后端 API URL
- [ ] 等待 Vercel 部署完成
- [ ] 测试前端访问

---

## ✅ 域名配置

- [ ] 在 Cloudflare 添加域名
- [ ] 配置 DNS 指向：
  - [ ] `api` → Render 后端
  - [ ] `www` → Vercel 前端
- [ ] 启用 Cloudflare SSL（免费）

---

## ✅ 测试验证

- [ ] 测试用户注册功能
- [ ] 测试用户登录功能
- [ ] 测试用户资料编辑
- [ ] 测试基础推荐功能
- [ ] 测试聊天功能（如果已实现）

---

## ✅ 监控配置

- [ ] 配置 Supabase 监控
- [ ] 配置 Render 日志查看
- [ ] （可选）配置 Sentry 错误跟踪
- [ ] （可选）配置 Uptime 监控

---

## 📊 部署信息记录

### 后端
```
Render URL: ___________________
GitHub 仓库: _________________
Render Service ID: ___________
```

### 数据库
```
Supabase Project URL: _______________
Database Connection String: _______
```

### 前端
```
Vercel URL: ____________________
GitHub 仓库: _________________
```

### 域名
```
主域名: ______________________
API 子域名: ________________
前端子域名: ________________
```

---

## 🎯 部署后下一步

1. 访问相亲网站前端
2. 测试核心功能
3. 收集用户反馈
4. 根据反馈优化功能
5. 规划下一阶段开发

---

## 📞 遇到问题？

- Render 部署失败：https://render.com/docs
- Supabase 连接问题：https://supabase.com/docs
- Vercel 部署问题：https://vercel.com/docs

---

**部署日期**: _______________
**部署人**: _______________
