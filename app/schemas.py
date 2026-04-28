"""
Pydantic 数据校验模型
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any
from datetime import date, datetime


# ========== Auth ==========
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nickname: str
    gender: int
    birth_date: Optional[str] = None
    city: Optional[str] = None
    bio: Optional[str] = None
    tags: Optional[str] = "[]"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ========== User ==========
class UserOut(BaseModel):
    id: int
    email: Optional[str]
    nickname: Optional[str]
    avatar_url: Optional[str]
    gender: int
    birthday: Optional[date]
    city_id: Optional[int]
    status: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserProfileOut(BaseModel):
    height: Optional[int]
    weight: Optional[int]
    education: Optional[int]
    occupation: Optional[str]
    income_level: Optional[int]
    self_intro: Optional[str]
    tags: Optional[List[str]]
    mbti: Optional[str]
    is_verified: bool

    class Config:
        from_attributes = True


class MeResponse(BaseModel):
    id: int
    email: Optional[str]
    nickname: Optional[str]
    avatar_url: Optional[str]
    gender: int
    birthday: Optional[date]
    profile: Optional[UserProfileOut]


class UpdateMeRequest(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[int] = None
    birthday: Optional[str] = None
    city: Optional[str] = None
    bio: Optional[str] = None
    tags: Optional[str] = None


class DiscoverResponse(BaseModel):
    users: List[dict]


# ========== Match ==========
class LikeRequest(BaseModel):
    to_user_id: int


class LikeResponse(BaseModel):
    matched: bool
    match_id: Optional[int] = None


class MatchOut(BaseModel):
    id: int
    user: dict
    match_score: Optional[float]
    status: int
    created_at: Optional[datetime]


class MatchesResponse(BaseModel):
    matches: List[MatchOut]


# ========== Chat ==========
class ConversationOut(BaseModel):
    id: int
    match_id: int
    other_user: dict
    last_message: Optional[str]
    last_message_at: Optional[datetime]
    unread_count: int


class ConversationsResponse(BaseModel):
    conversations: List[ConversationOut]


class MessageOut(BaseModel):
    id: int
    sender_id: int
    content: Optional[str]
    created_at: Optional[datetime]
    is_read: bool


class MessagesResponse(BaseModel):
    messages: List[MessageOut]


class SendMessageRequest(BaseModel):
    conversation_id: str
    content: str
