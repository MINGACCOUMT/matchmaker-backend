"""
标签管理 API（v1）

提供用户标签的独立 CRUD 端点，以及系统预定义标签查询。
"""
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.db.models import User, UserProfile
from app.schemas import SystemTagsResponse, TagAddRequest, TagsResponse, TagsUpdateRequest

router = APIRouter(prefix="/tags", tags=["tags"])


# 系统预定义的热门标签（可扩展为从数据库或缓存读取）
SYSTEM_TAGS = [
    "运动", "健身", "跑步", "游泳", "瑜伽",
    "旅行", "摄影", "音乐", "电影", "阅读",
    "美食", "烹饪", "游戏", "动漫", "宠物",
    "户外", "登山", "露营", "钓鱼", "滑雪",
    "艺术", "绘画", "舞蹈", "乐器", "唱歌",
    "科技", "编程", "投资", "理财", "创业",
    "公益", "环保", "手工", "园艺", "收藏",
    "咖啡", "茶道", "品酒", "烘焙", "火锅",
    "篮球", "足球", "羽毛球", "乒乓球", "网球",
    "电竞", "桌游", "剧本杀", "密室逃脱", "KTV",
]

POPULAR_TAGS = [
    "旅行", "美食", "音乐", "电影", "运动",
    "摄影", "阅读", "宠物", "游戏", "户外",
]


def _parse_tags(value) -> list:
    """将数据库中的 tags 字段解析为字符串列表。"""
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    try:
        parsed = json.loads(value)
        return [str(item) for item in parsed] if isinstance(parsed, list) else []
    except Exception:
        return []


def _serialize_tags(tags: list) -> str:
    """将标签列表序列化为 JSON 字符串存入数据库。"""
    if not tags:
        return "[]"
    return json.dumps([str(t).strip() for t in tags if str(t).strip()], ensure_ascii=False)


def _get_or_create_profile(db: Session, user_id: int) -> UserProfile:
    """获取或创建用户资料。"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.flush()
    return profile


@router.get("/system", response_model=SystemTagsResponse)
def get_system_tags():
    """获取系统预定义标签列表和热门标签。"""
    return {
        "tags": SYSTEM_TAGS,
        "popular": POPULAR_TAGS,
    }


@router.get("/me", response_model=TagsResponse)
def get_my_tags(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户的标签列表。"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    tags = _parse_tags(profile.tags) if profile else []
    return {"tags": tags}


@router.put("/me", response_model=TagsResponse)
def update_my_tags(
    req: TagsUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """覆盖式更新当前用户的标签列表。"""
    profile = _get_or_create_profile(db, user.id)
    # 去重、限制数量（最多 20 个）、限制长度（每个标签最多 20 字符）
    cleaned = []
    seen = set()
    for tag in req.tags:
        tag = str(tag).strip()
        if tag and tag not in seen and len(tag) <= 20:
            cleaned.append(tag)
            seen.add(tag)
        if len(cleaned) >= 20:
            break
    profile.tags = _serialize_tags(cleaned)
    db.commit()
    return {"tags": cleaned}


@router.post("/me", response_model=TagsResponse)
def add_my_tag(
    req: TagAddRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """为当前用户添加一个标签（如果不存在）。"""
    profile = _get_or_create_profile(db, user.id)
    current = _parse_tags(profile.tags)
    tag = req.tag.strip()
    if not tag:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Tag cannot be empty")
    if len(tag) > 20:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Tag too long (max 20 chars)")
    if tag in current:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already exists")
    if len(current) >= 20:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Max 20 tags allowed")
    current.append(tag)
    profile.tags = _serialize_tags(current)
    db.commit()
    return {"tags": current}


@router.delete("/me/{tag}", response_model=TagsResponse)
def delete_my_tag(
    tag: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除当前用户的指定标签。"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    current = _parse_tags(profile.tags)
    if tag not in current:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    current.remove(tag)
    profile.tags = _serialize_tags(current)
    db.commit()
    return {"tags": current}
