"""
用户相关 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import User, UserProfile
from app.schemas import MeResponse, UpdateMeRequest, DiscoverResponse
from app.core.auth import get_current_user
import json
from datetime import datetime

router = APIRouter()


@router.get("/me", response_model=MeResponse)
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "gender": user.gender,
        "birthday": user.birthday,
        "profile": {
            "height": profile.height if profile else None,
            "weight": profile.weight if profile else None,
            "education": profile.education if profile else None,
            "occupation": profile.occupation if profile else None,
            "income_level": profile.income_level if profile else None,
            "self_intro": profile.self_intro if profile else None,
            "tags": profile.tags if profile else [],
            "mbti": profile.mbti if profile else None,
            "is_verified": profile.is_verified if profile else False,
        } if profile else None,
    }


@router.put("/me")
def update_me(req: UpdateMeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.nickname:
        user.nickname = req.nickname
    if req.avatar_url:
        user.avatar_url = req.avatar_url
    if req.gender is not None:
        user.gender = req.gender
    if req.birthday:
        user.birthday = req.birthday

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    if req.bio:
        profile.self_intro = req.bio
    if req.tags:
        try:
            profile.tags = json.loads(req.tags) if isinstance(req.tags, str) else req.tags
        except Exception:
            profile.tags = []

    db.commit()
    return {"success": True}


@router.get("/discover")
def discover_users(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 简单返回其他用户（排除自己）
    others = db.query(User).filter(User.id != user.id).limit(20).all()
    users = []
    for u in others:
        profile = db.query(UserProfile).filter(UserProfile.user_id == u.id).first()
        users.append({
            "id": u.id,
            "nickname": u.nickname,
            "avatar_url": u.avatar_url,
            "gender": u.gender,
            "age": calculate_age(u.birthday) if u.birthday else None,
            "bio": profile.self_intro if profile else None,
            "tags": profile.tags if profile else [],
        })
    return {"users": users}


def calculate_age(birthday):
    if not birthday:
        return None
    today = datetime.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
