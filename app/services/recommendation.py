"""
推荐服务模块

基于匹配算法为用户推荐候选对象，支持排序、分页和过滤。
"""
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.db.models import Match, User, UserPreference, UserProfile
from app.services.matching import compute_match_score, parse_tags


def get_recommended_users(
    db: Session,
    current_user: User,
    limit: int = 20,
    offset: int = 0,
    min_score: Optional[float] = None,
    exclude_liked: bool = True,
    gender_filter: bool = True,
) -> Tuple[List[dict], int]:
    """
    获取推荐给当前用户的候选用户列表。

    Args:
        db: 数据库会话
        current_user: 当前用户
        limit: 返回数量限制
        offset: 分页偏移
        min_score: 最低匹配分数过滤（None = 不过滤）
        exclude_liked: 是否排除已喜欢/已匹配的用户
        gender_filter: 是否只推荐异性用户

    Returns:
        (user_list, total_count)
        user_list: 包含匹配分数的用户字典列表，已按匹配分数降序排列
        total_count: 符合条件的总用户数（用于分页）
    """
    # 获取当前用户的偏好和资料
    current_pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    current_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    # 如果用户没有设置偏好，创建一个默认偏好
    if not current_pref:
        current_pref = UserPreference(user_id=current_user.id)

    # 构建基础查询：排除自己
    query = db.query(User).filter(User.id != current_user.id)

    # 性别过滤：推荐异性
    if gender_filter and current_user.gender:
        # gender: 1=男, 2=女 (常见约定)
        opposite_gender = 2 if current_user.gender == 1 else 1
        query = query.filter(User.gender == opposite_gender)

    # 排除已喜欢/已匹配的用户
    liked_user_ids = []
    if exclude_liked:
        liked_matches = db.query(Match).filter(
            (Match.user_a_id == current_user.id) | (Match.user_b_id == current_user.id)
        ).all()
        for m in liked_matches:
            other_id = m.user_b_id if m.user_a_id == current_user.id else m.user_a_id
            liked_user_ids.append(other_id)

    if liked_user_ids:
        query = query.filter(~User.id.in_(liked_user_ids))

    # 获取所有候选用户
    candidates = query.all()

    # 计算每个候选用户的匹配分数
    scored_users = []
    for candidate in candidates:
        profile = db.query(UserProfile).filter(UserProfile.user_id == candidate.id).first()
        score, reason = compute_match_score(candidate, profile, current_pref)

        # 最低分数过滤
        if min_score is not None and score < min_score:
            continue

        scored_users.append({
            "user": candidate,
            "profile": profile,
            "score": score,
            "reason": reason,
        })

    # 按匹配分数降序排列
    scored_users.sort(key=lambda x: x["score"], reverse=True)

    total_count = len(scored_users)

    # 分页
    paged_users = scored_users[offset:offset + limit]

    # 构建返回结果
    result = []
    from app.api.v1.endpoints.users import calculate_age as api_calculate_age

    for item in paged_users:
        u = item["user"]
        p = item["profile"]
        result.append({
            "id": u.id,
            "nickname": u.nickname,
            "avatar_url": u.avatar_url,
            "gender": u.gender,
            "age": api_calculate_age(u.birthday),
            "city_id": u.city_id,
            "bio": p.self_intro if p else None,
            "tags": parse_tags(p.tags if p else None),
            "height": p.height if p else None,
            "education": p.education if p else None,
            "income_level": p.income_level if p else None,
            "match_score": item["score"],
            "match_reason": item["reason"],
        })

    return result, total_count
