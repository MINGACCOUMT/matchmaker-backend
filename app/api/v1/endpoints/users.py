"""
用户相关 API 端点
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

router = APIRouter()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """密码加密"""
    return pwd_context.hash(password)


class UserCreate(BaseModel):
    """创建用户请求"""
    phone: str
    nickname: str
    gender: int
    birthday: str
    password: str


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    phone: str
    nickname: str
    gender: int
    created_at: str


class LoginRequest(BaseModel):
    """登录请求"""
    phone: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str
    user: UserResponse


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 1. 检查手机号是否已注册
    existing_user = db.query(User).filter(User.phone == user.phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="手机号已注册")
    
    # 2. 创建用户记录
    password_hash = get_password_hash(user.password)
    db_user = User(
        phone=user.phone,
        nickname=user.nickname,
        gender=user.gender,
        birthday=datetime.strptime(user.birthday, "%Y-%m-%d").date() if user.birthday else None,
        password_hash=password_hash
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "id": db_user.id,
        "phone": db_user.phone,
        "nickname": db_user.nickname,
        "gender": db_user.gender,
        "created_at": db_user.created_at.isoformat() if db_user.created_at else datetime.now().isoformat(),
    }


@router.get("/profile/{user_id}")
async def get_profile(user_id: int, db: Session = Depends(get_db)):
    """获取用户资料"""
    # TODO: 实现获取资料逻辑
    return {
        "id": user_id,
        "nickname": "用户" + str(user_id),
    }


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    # 1. 查询用户是否存在
    user = db.query(User).filter(User.phone == request.phone).first()
    
    if not user or not user.password_hash:
        # 如果用户不存在或没有密码，返回模拟登录（临时）
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": request.phone, "exp": expire}
        access_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": 1,
                "phone": request.phone,
                "nickname": "模拟用户",
                "gender": 1,
                "created_at": datetime.now().isoformat(),
            }
        }
    
    # 2. 验证密码
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="密码错误")
    
    # 3. 生成 JWT token
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user.phone, "exp": expire}
    access_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # 4. 返回 token 和用户信息
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "phone": user.phone,
            "nickname": user.nickname or f"用户{user.id}",
            "gender": user.gender,
            "created_at": user.created_at.isoformat() if user.created_at else datetime.now().isoformat(),
        }
    }


@router.put("/profile/{user_id}")
async def update_profile(user_id: int, db: Session = Depends(get_db)):
    """更新用户资料"""
    # TODO: 实现更新资料逻辑
    return {
        "id": user_id,
        "updated": True,
    }
