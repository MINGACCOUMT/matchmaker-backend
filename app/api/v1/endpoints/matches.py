"""
匹配相关 API 端点
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.db.models import Chat, Match, User, UserProfile
from app.schemas import LikeRequest, LikeResponse, MatchOut, MatchesResponse

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/like", response_model=LikeResponse)
def like_user(req: LikeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """喜欢某个用户；如果对方已喜欢我，则将状态升级为匹配成功。"""
    # 检查是否喜欢自己
    if req.to_user_id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot like yourself")

    # 查询目标用户是否存在
    target = db.query(User).filter(User.id == req.to_user_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")

    # 查询是否已有匹配记录
    existing = db.query(Match).filter(
        ((Match.user_a_id == user.id) & (Match.user_b_id == req.to_user_id)) |
        ((Match.user_a_id == req.to_user_id) & (Match.user_b_id == user.id))
    ).first()

    matched = False
    match_id = None
    match_record = existing

    try:
        if existing:
            # 对方先喜欢我时，当前操作代表互相喜欢
            if existing.status == 0 and existing.user_b_id == user.id:
                now = datetime.utcnow()
                existing.status = 1  # 升级为匹配成功
                matched = True
                match_id = existing.id
                db.add(Chat(
                    match_id=existing.id,
                    user_a_id=existing.user_a_id,
                    user_b_id=existing.user_b_id,
                    is_active=True,
                    created_at=now,
                    last_message_at=now,
                ))
        else:
            # 创建新的喜欢记录
            match_record = Match(
                user_a_id=user.id,
                user_b_id=req.to_user_id,
                status=0,
                match_score=0.0,
                initiated_by=user.id,
                created_at=datetime.utcnow(),
            )
            db.add(match_record)
            db.flush()
            match_id = match_record.id
            matched = False

        # 更新当前用户最后活跃时间
        user.last_active_at = datetime.utcnow()
        db.commit()
        if existing:
            db.refresh(existing)
        elif match_record is not None:
            db.refresh(match_record)

        return {"matched": matched, "match_id": match_id}

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save like"
        ) from exc


@router.get("/", response_model=MatchesResponse)
def get_matches(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户所有已匹配成功的记录。"""
    matches = db.query(Match).filter(
        ((Match.user_a_id == user.id) | (Match.user_b_id == user.id)) &
        (Match.status == 1)
    ).all()

    result = []
    for match in matches:
        other_id = match.user_b_id if match.user_a_id == user.id else match.user_a_id
        other = db.query(User).filter(User.id == other_id).first()
        if other:
            profile = db.query(UserProfile).filter(UserProfile.user_id == other.id).first()
            result.append({
                "id": match.id,
                "user": {
                    "id": other.id,
                    "nickname": other.nickname,
                    "avatar_url": other.avatar_url,
                },
                "match_score": float(match.match_score) if match.match_score is not None else 85.0,
                "status": match.status,
                "created_at": match.created_at.isoformat(),
            })

    return {"matches": result}
