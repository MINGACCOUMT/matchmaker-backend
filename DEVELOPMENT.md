# Matchmaker 后端开发大纲

## 📊 项目状态

| 模块 | 状态 | 说明 |
|------|------|------|
| **主应用** | 🟡 70% | FastAPI 基础有了，CORS 已配置 |
| **路由** | 🟡 60% | auth 路由已注册，v1 路由部分注册 |
| **数据模型** | 🟡 80% | models.py 定义完整，需要检查外键 |
| **认证逻辑** | 🟢 50% | 基础注册/登录已实现（email 方式）|
| **匹配功能** | 🔴 0% | 路由存在但逻辑未实现（mock 数据）|
| **聊天功能** | 🔴 0% | 路由存在但逻辑未实现（mock 数据）|

---

## 🎯 开发阶段

### 阶段 1：后端基础修复 ⏳ 进行中

#### 任务清单

**后端修复（8 个任务）**

- [ ] 修复路由导入冲突（main.py 中 app.api.endpoints vs app.api.v1.endpoints）
- [ ] 检查并修复 models.py 外键关系（UserProfile.user_id, UserPreference.user_id）
- [ ] 统一认证方式（全部使用 email，移除 phone 相关代码）
- [ ] 完善 auth.py 逻辑（添加更详细的错误处理）
- [ ] 完善 users.py 的 /me 和 /discover 端点
- [ ] 完善 matches.py 的 /like 和 /matches 端点
- [ ] 完善 chat.py 的 WebSocket 支持或轮询机制

---

### 阶段 2：核心功能实现 ⏸️ 未开始

#### 任务清单

- [ ] 实现完整的匹配算法（基于用户偏好计算匹配分数）
- [ ] 实现匹配状态管理（喜欢、互相喜欢、匹配）
- [ ] 实现聊天消息存储和检索
- [ ] 添加用户头像上传功能
- [ ] 添加用户标签管理功能
- [ ] 实现推荐算法（基于标签和位置）

---

### 阶段 3：优化和部署 ⏸️ 未开始

#### 任务清单

- [ ] 添加 API 文档（Swagger/OpenAPI）
- [ ] 添加日志记录和错误监控
- [ ] 优化数据库查询（添加索引）
- [ ] 实现 Redis 缓存（会话和匹配结果）
- [ ] 性能优化
- [ ] 安全审计（输入验证、SQL 注入防护）

---

## 📋 详细任务说明

### 阶段 1：后端基础修复

#### 任务 1.1：修复路由导入冲突

**问题**：main.py 中同时导入了 `app.api.v1.endpoints` 和 `app.api.endpoints`

**当前代码**：
```python
from app.api.v1.endpoints import users, matches
from app.api.endpoints import auth, chat
```

**修复方案**：
- 只使用 `app.api.v1.endpoints`
- 移除 `app.api.endpoints` 的导入（废弃版本）
- 确保所有路由都使用 v1 前缀

---

#### 任务 1.2：检查并修复 models.py 外键关系

**问题**：UserProfile 和 UserPreference 的 user_id 可能缺少外键约束

**当前代码**：
```python
class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, primary_key=True)
    # ...
```

**修复方案**：
- 将 `primary_key=True` 改为 `ForeignKey('users.id')`
- 正确导入 `from sqlalchemy import Column, Integer, String, ForeignKey`

---

#### 任务 1.3：统一认证方式

**问题**：可能有 phone 和 email 两种认证方式

**修复方案**：
- 移除所有 phone 相关的代码
- 统一使用 email 认证
- 确保 RegisterRequest 和 LoginRequest 只包含 email 和 password

---

#### 任务 1.4：完善 auth.py

**当前功能**：
- ✅ 用户注册（email 方式）
- ✅ 用户登录（email 方式）
- ✅ JWT token 生成

**需要完善**：
- 添加更详细的错误处理（邮箱格式验证、密码强度）
- 添加邮箱验证码发送（可选）
- 添加登录失败次数限制（防暴力破解）

---

#### 任务 1.5：完善 users.py

**当前功能**：
- ✅ 注册端点
- ✅ 登录端点
- ❌ /me 端点（获取当前用户）
- ❌ /discover 端点（推荐用户列表）

**需要实现**：
- GET /api/v1/users/me - 返回当前用户资料
- PUT /api/v1/users/me - 更新用户资料
- GET /api/v1/users/discover - 返回推荐用户列表

---

#### 任务 1.6：完善 matches.py

**当前功能**：
- ❌ /like 端点（未实现）
- ❌ /matches 端点（未实现）

**需要实现**：
- POST /api/v1/matches/like - 喜欢某个用户
- GET /api/v1/matches/ - 获取我的匹配列表
- 匹配状态管理（pending, matched, rejected）

---

#### 任务 1.7：完善 chat.py

**当前功能**：
- ❌ /conversations 端点（未实现）
- ❌ /messages/{id} 端点（未实现）
- ❌ WebSocket 支持（未实现）

**需要实现**：
- GET /api/v1/chat/conversations - 获取会话列表
- GET /api/v1/chat/messages/{id} - 获取消息历史
- POST /api/v1/chat/send - 发送消息
- 考虑 WebSocket vs 轮询机制

---

## 📊 当前进度

| 阶段 | 进度 | 说明 |
|------|------|------|
| **阶段 1：基础修复** | 0% | 0/8 任务完成 |
| **阶段 2：核心功能** | 0% | 未开始 |
| **阶段 3：优化部署** | 0% | 未开始 |

---

## 📁 项目结构

```
/data/workspace/matchmaker-backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── core/
│   │   ├── config.py       # 配置管理
│   │   └── auth.py         # JWT 认证
│   ├── db/
│   │   ├── database.py     # 数据库连接
│   │   └── models.py       # 数据模型（待修复）
│   ├── api/
│   │   ├── v1/
│   │   │   └── endpoints/
│   │   │       ├── users.py   # 用户端点
│   │   │       ├── matches.py # 匹配端点
│   │   │       └── chat.py    # 聊天端点
│   │   └── endpoints/
│   │       └── auth.py         # 认证端点
│   └── schemas.py           # Pydantic 模型
├── migrations/               # 数据库迁移
└── requirements.txt
```

---

## 🚀 开始开发

**推荐顺序**：
1. 任务 1.1：修复路由导入冲突（最高优先级）
2. 任务 1.2：检查并修复 models.py 外键关系
3. 任务 1.3：统一认证方式（email）
4. 任务 1.4 - 1.7：完善各个端点

---

**后端开发大纲已创建！请告诉我从哪个任务开始。** 🚀
