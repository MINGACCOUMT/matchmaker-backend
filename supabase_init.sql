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
