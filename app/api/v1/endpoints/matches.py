"""
匹配相关 API 端点
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class MatchRequest(BaseModel):
    """匹配请求"""
    user_id: int
    limit: int = 10


class MatchResponse(BaseModel):
    """匹配响应"""
    user_id: int
    matched_users: List[dict]


@router.post("/find", response_model=MatchResponse)
async def find_matches(request: MatchRequest):
    """查找匹配"""
    # TODO: 实现匹配算法
    # 1. 查询用户的择偶条件
    # 2. 查询符合条件的其他用户
    # 3. 计算匹配度
    # 4. 返回推荐列表

    # 临时返回模拟数据
    return {
        "user_id": request.user_id,
        "matched_users": [
            {"id": 2, "nickname": "用户2", "score": 85.5},
            {"id": 3, "nickname": "用户3", "score": 82.3},
        ],
    }


@router.post("/like/{user_id}/{target_id}")
async def like_user(user_id: int, target_id: int):
    """喜欢用户"""
    # TODO: 实现喜欢逻辑
    return {
        "user_id": user_id,
        "target_id": target_id,
        "liked": True,
    }
