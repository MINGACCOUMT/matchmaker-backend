"""
数据库模型
"""
from sqlalchemy import Column, Integer, String, SmallInteger, Date, DateTime, Text, DECIMAL, Boolean
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255))
    nickname = Column(String(50))
    avatar_url = Column(String(500))
    gender = Column(SmallInteger, default=0)
    birthday = Column(Date)
    city_id = Column(Integer)
    status = Column(SmallInteger, default=0)
    last_active_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class UserProfile(Base):
    """用户资料表"""
    __tablename__ = "user_profiles"
    
    user_id = Column(Integer, primary=True)
    height = Column(SmallInteger)
    weight = Column(SmallInteger)
    education = Column(SmallInteger, default=0)
    occupation = Column(String(100))
    income_level = Column(SmallInteger)
    self_intro = Column(Text)
    tags = Column(Text)  # PostgreSQL数组，暂存为TEXT
    mbti = Column(String(4))
    profile_completion_rate = Column(SmallInteger, default=0)
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class UserPreference(Base):
    """用户择偶条件表"""
    __tablename__ = "user_preferences"
    
    user_id = Column(Integer, primary=True)
    min_age = Column(SmallInteger, default=18)
    max_age = Column(SmallInteger, default=99)
    min_height = Column(SmallInteger, default=140)
    max_height = Column(SmallInteger, default=220)
    education_level = Column(SmallInteger)
    city_ids = Column(Text)  # PostgreSQL数组，暂存为TEXT
    income_min = Column(SmallInteger)
    tags = Column(Text)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Match(Base):
    """匹配记录表"""
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_a_id = Column(Integer, index=True)
    user_b_id = Column(Integer, index=True)
    match_score = Column(DECIMAL(5, 2))
    match_reason = Column(Text)  # JSONB，暂存为TEXT
    status = Column(SmallInteger, default=0, index=True)
    initiated_by = Column(SmallInteger)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class Chat(Base):
    """聊天会话表"""
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer)
    user_a_id = Column(Integer)
    user_b_id = Column(Integer)
    last_message_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Message(Base):
    """消息记录表"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True)
    sender_id = Column(Integer)
    message_type = Column(SmallInteger, default=1)
    content = Column(Text)
    media_url = Column(String(500))
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)
