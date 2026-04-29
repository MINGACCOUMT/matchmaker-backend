# Matchmaker 后端开发大纲

> 技术栈：FastAPI + SQLAlchemy + PostgreSQL (Supabase) + JWT
> 部署目标：Render
> 更新日期：2026-04-29

---

## 📊 当前进度总览

| Phase | 任务 | 状态 | 备注 |
|-------|------|------|------|
| Phase 1 | 基础修复（import、外键、路由注册） | ✅ 已完成 | 2026-04-29，已 push |
| Phase 2 | 后端核心功能（matches 实现） | ⏳ 未开始 | |
| Phase 3 | 测试与联调 | ⏳ 未开始 | |
| Phase 4 | 部署上线 | ⏳ 未开始 | |

---

## ✅ Phase 1：基础修复（DONE）

**完成时间**：2026-04-29
**分支**：`auto-code/20260428-222406`

### 改动内容

1. **修复 import 路径**
   - `app/api/endpoints/auth.py`: `app.models` → `app.db.models`
   - `app/api/endpoints/chat.py`: `app.models` → `app.db.models`
   - `app/core/auth.py`: `app.models` → `app.db.models`

2. **添加外键约束**
   - `app/db/models.py`: `UserProfile.user_id` 添加 `ForeignKey('users.id')`
   - `app/db/models.py`: `UserPreference.user_id` 添加 `ForeignKey('users.id')`

3. **注册路由**
   - `app/main.py`: 添加 `app.include_router(auth.router, prefix="/api/auth")`
   - `app/main.py`: 添加 `app.include_router(chat.router, prefix="/api/chat")`

4. **环境准备**
   - 创建 `venv/` 虚拟环境
   - 安装所有依赖（fastapi / sqlalchemy / python-jose / passlib / psycopg2-binary 等）
   - 验证通过：`python -c "from app.main import app"` → OK

---

## ⏳ Phase 2：后端核心功能实现

### 2.1 重写 `app/api/v1/endpoints/matches.py`

当前状态：只有 mock 数据，未连接数据库。

需要实现：

```
POST   /api/v1/matches/like        喜欢某个用户（需 JWT）
GET    /api/v1/matches             获取我的匹配列表（需 JWT）
```

**POST /like 逻辑**：
1. 从 JWT 获取当前用户 ID
2. 检查是否已存在 like 记录
3. 写入 `matches` 表（status=0 表示单向喜欢）
4. 检查对方是否也喜欢了我 → 如果是，更新 status=1（双向匹配）
5. 如果双向匹配，自动创建 chat 会话

**GET /matches 逻辑**：
1. 从 JWT 获取当前用户 ID
2. 查询 `matches` 表中 status=1 且涉及当前用户的记录
3. 返回对方用户资料 + 匹配时间

### 2.2 验证 `app/api/endpoints/chat.py`

当前状态：代码已有，但未完整测试。

需要确认：
- `GET /api/chat/conversations` 返回会话列表正常
- `GET /api/chat/messages/{conv_id}` 返回消息列表正常
- `POST /api/chat/messages` 发送消息正常
- 发送消息后是否更新 `chats.last_message_at`

### 2.3 CORS 配置补充

当前 `BACKEND_CORS_ORIGINS` 已包含生产域名，但缺少本地开发端口：
- 补充 `"http://localhost:3000"` 和 `"http://localhost:5173"`

### 2.4 环境变量配置

- 确认 `.env` / `.env.production` 中 `DATABASE_URL` 正确
- 确认 `SECRET_KEY` 在生产环境使用强随机值

---

## ⏳ Phase 3：测试与联调

### 3.1 后端冒烟测试

```bash
# 启动服务
source venv/bin/activate
uvicorn app.main:app --reload

# 测试端点
curl -X POST http://localhost:8000/api/auth/register -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"123456","nickname":"Test","gender":1}'

curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"123456"}'

curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/users/me

curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/users/discover

curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"to_user_id":2}' http://localhost:8000/api/v1/matches/like
```

### 3.2 数据库迁移

- 确认 `Base.metadata.create_all()` 能正确创建所有表
- 或配置 Alembic 做正式迁移

---

## ⏳ Phase 4：部署上线

### 4.1 Render 部署

- 推送代码到 GitHub `main` 分支
- Render 自动从 `main` 分支部署
- 确认环境变量（DATABASE_URL、SECRET_KEY）

### 4.2 部署后验证

- 访问 `https://matchmaker-api-bi2k.onrender.com/health`
- 测试注册/登录流程
- 确认 Swagger Docs (`/docs`) 正常

---

## 📁 项目结构

```
matchmaker-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 入口
│   ├── schemas.py              # Pydantic 模型
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── auth.py         # 注册/登录
│   │   │   ├── chat.py         # 聊天
│   │   │   └── __init__.py
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── users.py     # /me, /discover
│   │           └── matches.py   # /like, /matches (TODO)
│   ├── core/
│   │   ├── config.py           # 配置
│   │   └── auth.py             # JWT/密码工具
│   └── db/
│       ├── database.py         # SQLAlchemy 引擎
│       └── models.py           # 数据库模型
├── venv/                       # Python 虚拟环境
├── requirements.txt
├── Dockerfile
└── render.yaml
```

---

## 🔗 相关资源

- **GitHub**: https://github.com/MINGACCOUMT/matchmaker-backend
- **Render**: https://matchmaker-api-bi2k.onrender.com
- **Supabase**: https://lwormsunwjwlutwqnlnt.supabase.co
