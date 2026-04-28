# Supabase 数据库初始化指南

## 📋 初始化步骤

### 步骤 1：访问 Supabase Dashboard

```
https://supabase.com/dashboard
```

### 步骤 2：选择或创建项目

1. 如果已有项目，点击进入
2. 如果没有，点击 **"New Project"**：
   - **Name**: `matchmaker`
   - **Database Password**: 设置一个强密码
   - **Region**: `Southeast Asia (Singapore)`（与后端同区域）

### 步骤 3：打开 SQL Editor

1. 点击左侧菜单 **"SQL Editor"**
2. 点击 **"New Query"**

### 步骤 4：复制并运行 SQL 脚本

复制以下完整 SQL 脚本，粘贴到 SQL Editor 中：

```sql
-- Matchmaker Backend 数据库初始化脚本

-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    nickname VARCHAR(50),
    avatar_url VARCHAR(500),
    gender SMALLINT DEFAULT 0,
    birthday DATE,
    city_id INTEGER,
    status SMALLINT DEFAULT 0,
    last_active_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 用户资料表
CREATE TABLE user_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    height SMALLINT,
    weight SMALLINT,
    education SMALLINT DEFAULT 0,
    occupation VARCHAR(100),
    income_level SMALLINT,
    self_intro TEXT,
    tags TEXT[],
    mbti CHAR(4),
    profile_completion_rate SMALLINT DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 用户择偶条件
CREATE TABLE user_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    min_age SMALLINT DEFAULT 18,
    max_age SMALLINT DEFAULT 99,
    min_height SMALLINT DEFAULT 140,
    max_height SMALLINT DEFAULT 220,
    education_level SMALLINT,
    city_ids INTEGER[],
    income_min SMALLINT,
    tags TEXT[],
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 匹配记录
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    user_a_id INTEGER REFERENCES users(id),
    user_b_id INTEGER REFERENCES users(id),
    match_score DECIMAL(5,2),
    match_reason JSONB,
    status SMALLINT DEFAULT 0,
    initiated_by SMALLINT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 聊天会话
CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(id),
    user_a_id INTEGER REFERENCES users(id),
    user_b_id INTEGER REFERENCES users(id),
    last_message_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 消息记录
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER REFERENCES chats(id),
    sender_id INTEGER REFERENCES users(id),
    message_type SMALLINT DEFAULT 1,
    content TEXT,
    media_url VARCHAR(500),
    is_read BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_city ON users(city_id);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_matches_user_a ON matches(user_a_id);
CREATE INDEX idx_matches_user_b ON matches(user_b_id);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_messages_chat ON messages(chat_id);
CREATE INDEX idx_messages_created ON messages(created_at DESC);
```

### 步骤 5：点击运行

点击右上角 **"Run"** 或按 `Ctrl + Enter` 执行 SQL

### 步骤 6：验证表创建

在 SQL Editor 中运行以下查询验证：

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

**预期结果**：
```
table_name
----------
chats
matches
messages
user_preferences
user_profiles
users
```

---

## 📊 数据库表说明

| 表名 | 说明 | 主要字段 |
|------|------|---------|
| `users` | 用户基本信息 | id, phone, nickname, gender, birthday |
| `user_profiles` | 用户详细资料 | height, occupation, education |
| `user_preferences` | 用户择偶条件 | min_age, max_age, min_height |
| `matches` | 匹配记录 | user_a_id, user_b_id, match_score |
| `chats` | 聊天会话 | match_id, user_a_id, user_b_id |
| `messages` | 消息记录 | chat_id, sender_id, content |

---

## 🔧 数据库连接信息

项目已配置的连接字符串：

```
postgresql://postgres:L.am19961209..@db.lwormsunwjwlutwqnlnt.supabase.co:5432/postgres
```

**注意**：
- 如果是新创建的 Supabase 项目，需要更新连接字符串中的密码
- 在 Render Dashboard 中更新 `DATABASE_URL` 环境变量

---

## ⚠️ 重要提示

1. **备份数据库**
   - 定期备份数据
   - Supabase 提供自动备份

2. **访问控制**
   - 默认只允许应用访问
   - 勿在公网暴露数据库端口

3. **性能优化**
   - 已创建必要索引
   - 避免全表扫描查询

---

## 🎯 下一步

数据库初始化完成后：

1. ✅ 更新后端 DATABASE_URL（如果密码变化）
2. ✅ 测试后端连接数据库
3. ✅ 实现真实注册/登录功能
4. ✅ 开发匹配算法

---

**SQL 脚本已准备好，请在 Supabase Dashboard 中运行！** 🗄️
