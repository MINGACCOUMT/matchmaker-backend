"""
匹配相关 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import User, Match
from app.schemas import LikeRequest, LikeResponse, MatchesResponse
from app.core.auth import get_current_user
from datetime import datetime

router = APIRouter()


@router.post("/like")
def like_user(req: LikeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == req.to_user_id).first()
    if not target:
        return {"matched": False}

    # 检查是否已存在匹配
    existing = db.query(Match).filter(
        ((Match.user_a_id == user.id) & (Match.user_b_id == req.to_user_id)) |
        ((Match.user_a_id == req.to_user_id) & (Match.user_b_id == user.id))
    ).first()

    if existing:
        # 如果对方也喜欢了我，则匹配成功
        if existing.status == 0 and existing.user_b_id == user.id:
            existing.status = 1
            db.commit()
            return {"matched": True, "match_id": existing.id}
        return {"matched": existing.status == 1, "match_id": existing.id}

    # 创建新的喜欢记录
    match = Match(
        user_a_id=user.id,
        user_b_id=req.to_user_id,
        status=0,
        created_at=datetime.utcnow(),
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return {"matched": False, "match_id": match.id}


@router.get("/")
def get_matches(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    matches = db.query(Match).filter(
        ((Match.user_a_id == user.id) | (Match.user_b_id == user.id)) & (Match.status == 1)
    ).all()

    result = []
    for m in matches:
        other_id = m.user_b_id if m.user_a_id == user.id else m.user_a_id
        other = db.query(User).filter(User.id == other_id).first()
        if other:
            result.append({
                "id": m.id,
                "user": {
                    "id": other.id,
                    "nickname": other.nickname,
                    "avatar_url": other.avatar_url,
                },
                "match_score": float(m.match_score) if m.match_score else 85.0,
                "status": m.status,
                "created_at": m.created_at,
            })
    return {"matches": result}
