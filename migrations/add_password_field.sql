"""
数据库迁移脚本 - 添加密码字段到users表
"""

-- 添加密码字段到users表
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_users_password ON users(password_hash);
