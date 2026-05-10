"""
匹配算法模块

基于用户偏好（年龄、身高、教育、收入、城市、标签）计算匹配分数。
"""
import json
from datetime import date
from typing import List, Optional, Tuple

from app.db.models import User, UserProfile, UserPreference


# ========== 常量定义 ==========

# 各维度权重（总和应为 1.0）
WEIGHT_AGE = 0.20
WEIGHT_HEIGHT = 0.15
WEIGHT_EDUCATION = 0.15
WEIGHT_INCOME = 0.15
WEIGHT_CITY = 0.15
WEIGHT_TAGS = 0.20

# 教育等级映射
EDUCATION_LEVELS = {
    0: 0,   # 未设置
    1: 1,   # 高中
    2: 2,   # 大专
    3: 3,   # 本科
    4: 4,   # 硕士
    5: 5,   # 博士
}

# 收入等级映射
INCOME_LEVELS = {
    0: 0,   # 未设置
    1: 1,   # < 5K
    2: 2,   # 5K-10K
    3: 3,   # 10K-20K
    4: 4,   # 20K-50K
    5: 5,   # > 50K
}


def calculate_age(birthday: Optional[date]) -> Optional[int]:
    """根据生日计算年龄。"""
    if not birthday:
        return None
    today = date.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))


def parse_tags(value) -> List[str]:
    """将标签解析为字符串列表，兼容 JSON 字符串和数组。"""
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    try:
        parsed = json.loads(value)
        return [str(item) for item in parsed] if isinstance(parsed, list) else []
    except Exception:
        return []


def parse_city_ids(value) -> List[int]:
    """将城市 ID 解析为整数列表。"""
    if not value:
        return []
    if isinstance(value, list):
        return [int(item) for item in value if str(item).isdigit()]
    try:
        parsed = json.loads(value)
        return [int(item) for item in parsed if str(item).isdigit()] if isinstance(parsed, list) else []
    except Exception:
        return []


# ========== 单项评分函数 ==========

def score_age(target_age: Optional[int], pref: UserPreference) -> float:
    """
    年龄匹配评分。
    在 [min_age, max_age] 范围内得满分，超出范围按距离线性衰减。
    """
    if target_age is None:
        return 50.0  # 未知年龄给中等分
    min_age = pref.min_age or 18
    max_age = pref.max_age or 99
    if min_age <= target_age <= max_age:
        return 100.0
    # 超出范围的惩罚
    if target_age < min_age:
        diff = min_age - target_age
    else:
        diff = target_age - max_age
    # 每差1岁扣5分，最低0分
    return max(0.0, 100.0 - diff * 5.0)


def score_height(target_height: Optional[int], pref: UserPreference) -> float:
    """
    身高匹配评分。
    在 [min_height, max_height] 范围内得满分，超出范围按距离线性衰减。
    """
    if target_height is None:
        return 50.0
    min_h = pref.min_height or 140
    max_h = pref.max_height or 220
    if min_h <= target_height <= max_h:
        return 100.0
    if target_height < min_h:
        diff = min_h - target_height
    else:
        diff = target_height - max_h
    # 每差1cm扣2分，最低0分
    return max(0.0, 100.0 - diff * 2.0)


def score_education(target_edu: Optional[int], pref: UserPreference) -> float:
    """
    教育水平匹配评分。
    目标教育 >= 偏好教育 = 满分，否则按差距扣分。
    """
    if target_edu is None:
        return 50.0
    pref_edu = pref.education_level
    if pref_edu is None or pref_edu == 0:
        return 100.0  # 无偏好 = 不扣分
    target_level = EDUCATION_LEVELS.get(target_edu, 0)
    pref_level = EDUCATION_LEVELS.get(pref_edu, 0)
    if target_level >= pref_level:
        return 100.0
    diff = pref_level - target_level
    return max(0.0, 100.0 - diff * 25.0)


def score_income(target_income: Optional[int], pref: UserPreference) -> float:
    """
    收入水平匹配评分。
    目标收入 >= 偏好最低收入 = 满分，否则按差距扣分。
    """
    if target_income is None:
        return 50.0
    pref_min = pref.income_min
    if pref_min is None or pref_min == 0:
        return 100.0
    target_level = INCOME_LEVELS.get(target_income, 0)
    pref_level = INCOME_LEVELS.get(pref_min, 0)
    if target_level >= pref_level:
        return 100.0
    diff = pref_level - target_level
    return max(0.0, 100.0 - diff * 20.0)


def score_city(target_city_id: Optional[int], pref: UserPreference) -> float:
    """
    城市匹配评分。
    目标城市在偏好城市列表中 = 满分，否则 0 分。
    """
    if target_city_id is None:
        return 50.0
    pref_cities = parse_city_ids(pref.city_ids)
    if not pref_cities:
        return 100.0  # 无城市偏好 = 不扣分
    if target_city_id in pref_cities:
        return 100.0
    return 0.0


def score_tags(target_tags: List[str], pref: UserPreference) -> float:
    """
    标签匹配评分。
    基于共同标签数量计算 Jaccard 相似度。
    """
    if not target_tags:
        return 50.0
    pref_tags = parse_tags(pref.tags)
    if not pref_tags:
        return 100.0  # 无标签偏好 = 不扣分
    # 计算交集
    common = set(target_tags) & set(pref_tags)
    if not common:
        return 0.0
    # Jaccard 相似度
    union = set(target_tags) | set(pref_tags)
    jaccard = len(common) / len(union)
    return jaccard * 100.0


# ========== 综合匹配分数计算 ==========

def compute_match_score(
    target_user: User,
    target_profile: Optional[UserProfile],
    preference: UserPreference
) -> Tuple[float, str]:
    """
    计算目标用户相对于当前用户偏好的匹配分数。

    Returns:
        (match_score, match_reason)
        match_score: 0-100 的浮点数
        match_reason: 匹配原因描述（JSON 字符串）
    """
    target_age = calculate_age(target_user.birthday)
    target_height = target_profile.height if target_profile else None
    target_edu = target_profile.education if target_profile else None
    target_income = target_profile.income_level if target_profile else None
    target_city = target_user.city_id
    target_tags = parse_tags(target_profile.tags if target_profile else None)

    # 计算各维度得分
    age_score = score_age(target_age, preference)
    height_score = score_height(target_height, preference)
    edu_score = score_education(target_edu, preference)
    income_score = score_income(target_income, preference)
    city_score = score_city(target_city, preference)
    tags_score = score_tags(target_tags, preference)

    # 加权总分
    total_score = (
        age_score * WEIGHT_AGE +
        height_score * WEIGHT_HEIGHT +
        edu_score * WEIGHT_EDUCATION +
        income_score * WEIGHT_INCOME +
        city_score * WEIGHT_CITY +
        tags_score * WEIGHT_TAGS
    )

    # 构建匹配原因
    reasons = {
        "age": {"score": round(age_score, 1), "weight": WEIGHT_AGE},
        "height": {"score": round(height_score, 1), "weight": WEIGHT_HEIGHT},
        "education": {"score": round(edu_score, 1), "weight": WEIGHT_EDUCATION},
        "income": {"score": round(income_score, 1), "weight": WEIGHT_INCOME},
        "city": {"score": round(city_score, 1), "weight": WEIGHT_CITY},
        "tags": {"score": round(tags_score, 1), "weight": WEIGHT_TAGS},
        "total": round(total_score, 1),
    }

    return round(total_score, 2), json.dumps(reasons, ensure_ascii=False)


def compute_bidirectional_score(
    user_a: User,
    profile_a: Optional[UserProfile],
    pref_a: UserPreference,
    user_b: User,
    profile_b: Optional[UserProfile],
    pref_b: UserPreference,
) -> Tuple[float, str]:
    """
    计算双向匹配分数（A对B的偏好 + B对A的偏好，取平均）。

    Returns:
        (match_score, match_reason)
    """
    score_a, reason_a = compute_match_score(user_b, profile_b, pref_a)
    score_b, reason_b = compute_match_score(user_a, profile_a, pref_b)

    total = (score_a + score_b) / 2.0

    reasons = {
        "user_a_to_b": json.loads(reason_a),
        "user_b_to_a": json.loads(reason_b),
        "bidirectional_score": round(total, 1),
    }

    return round(total, 2), json.dumps(reasons, ensure_ascii=False)
