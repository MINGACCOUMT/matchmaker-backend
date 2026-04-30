"""
批量操作 API
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.db.models import Match, User

router = APIRouter(prefix="/swipe", tags=["swipe"])


@router.post("/batch-like")
async def batch_like(
    match_ids: list[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量喜欢
    """
    if not match_ids:
        raise HTTPException(status_code=400, detail="请提供 match_ids")
    
    # 批量创建匹配
    created_count = 0
    for match_id in match_ids:
        # 检查是否已存在
        existing = db.query(Match).filter(
            Match.user_a_id == current_user.id,
            Match.user_b_id == match_id,
            Match.status >= 0
        ).first()

        if not existing:
            new_match = Match(
                user_a_id=current_user.id,
                user_b_id=match_id,
                status=0,
                created_at=datetime.utcnow()
            )
            db.add(new_match)
            created_count += 1
    
    db.commit()
    
    return {
        "message": f"成功创建 {created_count} 个匹配",
        "created_count": created_count
    }


@router.post("/batch-unlike")
async def batch_unlike(
    match_ids: list[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量取消匹配
    """
    if not match_ids:
        raise HTTPException(status_code=400, detail="请提供 match_ids")
    
    # 批量取消匹配
    updated_count = 0
    for match_id in match_ids:
        # 查找匹配
        match = db.query(Match).filter(
            or_(
                (Match.user_a_id == current_user.id) & (Match.user_b_id == match_id),
                (Match.user_a_id == match_id) & (Match.user_b_id == current_user.id)
            ),
            Match.status >= 0
        ).first()

        if match:
            match.status = -1
            updated_count += 1
    
    db.commit()
    
    return {
        "message": f"成功取消 {updated_count} 个匹配",
        "updated_count": updated_count
    }


@router.get("/matches")
async def get_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取匹配列表
    """
    # 获取所有活跃匹配
    matches = db.query(Match).filter(
        or_(
            (Match.user_a_id == current_user.id),
            (Match.user_b_id == current_user.id)
        ),
        Match.status >= 0
    ).order_by(Match.created_at.desc()).all()
    
    # 获取匹配用户信息
    match_list = []
    for match in matches:
        other_id = match.user_b_id if match.user_a_id == current_user.id else match.user_a_id
        other = db.query(User).filter(User.id == other_id).first()
        
        if other:
            match_list.append({
                "id": match.id,
                "other_user": {
                    "id": other.id,
                    "nickname": other.nickname,
                    "avatar_url": other.avatar_url,
                    "gender": other.gender,
                    "birthday": other.birthday,
                },
                "created_at": match.created_at,
                "is_mutual": True  # 可以添加双向匹配检查
            })
    
    return {
        "matches": match_list,
        "count": len(match_list)
    }
