"""
用户相关 API 端点
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class UserCreate(BaseModel):
    """创建用户请求"""
    phone: str
    nickname: str
    gender: int
    birthday: str


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    phone: str
    nickname: str
    gender: int
    created_at: str


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # TODO: 实现注册逻辑
    # 1. 验证手机号格式
    # 2. 检查手机号是否已注册
    # 3. 创建用户记录
    # 4. 返回用户信息

    # 临时返回
    from datetime import datetime
    return {
        "id": 1,
        "phone": user.phone,
        "nickname": user.nickname,
        "gender": user.gender,
        "created_at": datetime.now().isoformat(),
    }


@router.get("/profile/{user_id}")
async def get_profile(user_id: int, db: Session = Depends(get_db)):
    """获取用户资料"""
    # TODO: 实现获取资料逻辑
    return {
        "id": user_id,
        "nickname": "用户" + str(user_id),
    }


@router.put("/profile/{user_id}")
async def update_profile(user_id: int, db: Session = Depends(get_db)):
    """更新用户资料"""
    # TODO: 实现更新资料逻辑
    return {
        "id": user_id,
        "updated": True,
    }
