"""
认证相关 API
"""
from datetime import datetime, date
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, get_password_hash, verify_password
from app.db.database import get_db
from app.db.models import User, UserProfile
from app.schemas import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # 检查邮箱是否已注册
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 解析 tags
    try:
        tags = json.loads(req.tags) if req.tags else []
    except Exception:
        tags = []

    # 转换 birth_date 为 date 对象
    birthday = None
    if req.birth_date:
        try:
            birthday = date.fromisoformat(req.birth_date)
        except ValueError:
            birthday = None

    # 创建用户
    user = User(
        email=req.email,
        password_hash=get_password_hash(req.password),
        nickname=req.nickname,
        gender=req.gender,
        birthday=birthday,
        status=1,
        last_active_at=datetime.utcnow(),
    )
    db.add(user)
    db.flush()  # 获取 user.id

    # 创建用户资料
    profile = UserProfile(
        user_id=user.id,
        self_intro=req.bio,
        tags=json.dumps(tags) if tags else None,
    )
    db.add(profile)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "gender": user.gender,
        },
    }


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    user.last_active_at = datetime.utcnow()
    db.commit()

    access_token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "gender": user.gender,
        },
    }
