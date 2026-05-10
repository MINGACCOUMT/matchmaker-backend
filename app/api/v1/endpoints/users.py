"""
用户 API（v1）

包含当前用户资料读取/更新和发现页用户列表。
所有接口默认使用 JWT 鉴权，通过 get_current_user 获取登录用户。
"""
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.db.models import User, UserProfile
from app.schemas import DiscoverResponse, MeResponse, UpdateMeRequest
from app.services.recommendation import get_recommended_users

router = APIRouter(prefix="/users", tags=["users"])


def calculate_age(birthday):
    """根据生日计算年龄；生日为空时返回 None。"""
    if not birthday:
        return None
    today = datetime.today().date()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))


def parse_tags(value):
    """将用户标签解析为字符串列表，兼容 JSON 字符串和数组。"""
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    try:
        parsed = json.loads(value)
        return [str(item) for item in parsed] if isinstance(parsed, list) else []
    except Exception:
        return []


@router.get("/me", response_model=MeResponse)
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前登录用户的基础信息和扩展资料。"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "gender": user.gender,
        "birthday": user.birthday,
        "city": user.city,
        "phone": user.phone,
        "address": user.address,
        "profile": {
            "height": profile.height if profile else None,
            "weight": profile.weight if profile else None,
            "education": profile.education if profile else None,
            "occupation": profile.occupation if profile else None,
            "income_level": profile.income_level if profile else None,
            "self_intro": profile.self_intro if profile else None,
            "tags": parse_tags(profile.tags) if profile else [],
            "mbti": profile.mbti if profile else None,
            "is_verified": profile.is_verified if profile else False,
        } if profile else None,
    }


@router.put("/me")
def update_me(req: UpdateMeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """更新当前登录用户资料；未传字段保持不变。"""
    if req.nickname is not None:
        user.nickname = req.nickname
    if req.avatar_url is not None:
        user.avatar_url = req.avatar_url
    if req.gender is not None:
        user.gender = req.gender
    if req.birthday is not None:
        try:
            from datetime import date
            user.birthday = date.fromisoformat(req.birthday)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="birthday must be YYYY-MM-DD") from exc
    if req.phone is not None:
        user.phone = req.phone
    if req.city is not None:
        user.city = req.city

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    if req.bio is not None:
        profile.self_intro = req.bio
    if req.tags is not None:
        profile.tags = json.dumps(parse_tags(req.tags), ensure_ascii=False)
    if req.address is not None:
        profile.address = req.address

    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update profile") from exc
    return {"success": True}


@router.get("/discover", response_model=DiscoverResponse)
def discover_users(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="分页偏移"),
    min_score: float = Query(None, ge=0, le=100, description="最低匹配分数"),
):
    """
    发现页：返回按匹配分数排序的候选用户列表。

    - 默认只推荐异性用户
    - 默认排除已喜欢/已匹配的用户
    - 按匹配分数从高到低排序
    - 支持分页
    """
    users, total = get_recommended_users(
        db=db,
        current_user=user,
        limit=limit,
        offset=offset,
        min_score=min_score,
        exclude_liked=True,
        gender_filter=True,
    )
    return {
        "users": users,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
