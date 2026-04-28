"""
SQLAlchemy 数据库模型
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, SmallInteger, Text, DECIMAL, JSON, ForeignKey, ARRAY
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    nickname = Column(String(50))
    avatar_url = Column(String(500))
    gender = Column(SmallInteger, default=0)
    birthday = Column(Date)
    city_id = Column(Integer)
    status = Column(SmallInteger, default=0)
    last_active_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    height = Column(SmallInteger)
    weight = Column(SmallInteger)
    education = Column(SmallInteger, default=0)
    occupation = Column(String(100))
    income_level = Column(SmallInteger)
    self_intro = Column(Text)
    tags = Column(ARRAY(String))
    mbti = Column(String(4))
    profile_completion_rate = Column(SmallInteger, default=0)
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    min_age = Column(SmallInteger, default=18)
    max_age = Column(SmallInteger, default=99)
    min_height = Column(SmallInteger, default=140)
    max_height = Column(SmallInteger, default=220)
    education_level = Column(SmallInteger)
    city_ids = Column(ARRAY(Integer))
    income_min = Column(SmallInteger)
    tags = Column(ARRAY(String))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user_a_id = Column(Integer, ForeignKey("users.id"))
    user_b_id = Column(Integer, ForeignKey("users.id"))
    match_score = Column(DECIMAL(5, 2))
    match_reason = Column(JSON)
    status = Column(SmallInteger, default=0)
    initiated_by = Column(SmallInteger)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    user_a_id = Column(Integer, ForeignKey("users.id"))
    user_b_id = Column(Integer, ForeignKey("users.id"))
    last_message_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    message_type = Column(SmallInteger, default=1)
    content = Column(Text)
    media_url = Column(String(500))
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
