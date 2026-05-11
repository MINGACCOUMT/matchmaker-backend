"""Tests for the matching algorithm and recommendation engine."""
import json
from datetime import date

import pytest

from app.db.database import get_db
from app.db.models import User, UserPreference, UserProfile
from app.services.matching import (
    calculate_age,
    compute_bidirectional_score,
    compute_match_score,
    parse_city_ids,
    parse_tags,
    score_age,
    score_city,
    score_education,
    score_height,
    score_income,
    score_tags,
)
from app.services.recommendation import get_recommended_users


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------
import uuid


@pytest.fixture
def db():
    """Provide a database session for service-layer tests."""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


def _make_unique_email(prefix="user"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def sample_user(db):
    """Create a sample user with profile and preference."""
    user = User(
        email=_make_unique_email("sample"),
        nickname="Sample",
        gender=1,
        birthday=date(1990, 6, 15),
        city_id=1,
        status=1,
    )
    db.add(user)
    db.flush()

    profile = UserProfile(
        user_id=user.id,
        height=175,
        education=3,  # 本科
        income_level=3,  # 10K-20K
        tags=json.dumps(["旅行", "摄影", "美食"]),
    )
    db.add(profile)

    preference = UserPreference(
        user_id=user.id,
        min_age=22,
        max_age=32,
        min_height=160,
        max_height=185,
        education_level=2,  # 大专及以上
        income_min=2,  # 5K+
        city_ids=json.dumps([1, 2]),
        tags=json.dumps(["旅行", "音乐"]),
    )
    db.add(preference)
    db.commit()

    return user


@pytest.fixture
def target_user(db):
    """Create a target user that matches preferences well."""
    user = User(
        email=_make_unique_email("target"),
        nickname="Target",
        gender=2,
        birthday=date(1995, 3, 20),
        city_id=1,
        status=1,
    )
    db.add(user)
    db.flush()

    profile = UserProfile(
        user_id=user.id,
        height=168,
        education=3,  # 本科
        income_level=3,  # 10K-20K
        tags=json.dumps(["旅行", "音乐", "电影"]),
    )
    db.add(profile)
    db.commit()

    return user


@pytest.fixture
def mismatched_user(db):
    """Create a user that does NOT match preferences well."""
    user = User(
        email=_make_unique_email("mismatch"),
        nickname="Mismatch",
        gender=2,
        birthday=date(2005, 1, 1),  # 太年轻
        city_id=99,  # 不同城市
        status=1,
    )
    db.add(user)
    db.flush()

    profile = UserProfile(
        user_id=user.id,
        height=150,  # 太矮
        education=1,  # 高中
        income_level=1,  # <5K
        tags=json.dumps(["游戏", "动漫"]),
    )
    db.add(profile)
    db.commit()

    return user


# ---------------------------------------------------------------------------
# Unit tests for scoring functions
# ---------------------------------------------------------------------------
def test_calculate_age():
    birthday = date(1990, 6, 15)
    age = calculate_age(birthday)
    today = date.today()
    expected = today.year - 1990 - ((today.month, today.day) < (6, 15))
    assert age == expected


def test_calculate_age_none():
    assert calculate_age(None) is None


def test_parse_tags_json():
    assert parse_tags('["a", "b"]') == ["a", "b"]


def test_parse_tags_list():
    assert parse_tags(["a", "b"]) == ["a", "b"]


def test_parse_tags_empty():
    assert parse_tags(None) == []
    assert parse_tags("") == []


def test_parse_city_ids():
    assert parse_city_ids('[1, 2, 3]') == [1, 2, 3]
    assert parse_city_ids(None) == []


def test_score_age_perfect():
    pref = UserPreference(min_age=22, max_age=32)
    assert score_age(25, pref) == 100.0


def test_score_age_outside():
    pref = UserPreference(min_age=22, max_age=32)
    assert score_age(18, pref) == 80.0  # 22-18=4, 4*5=20, 100-20=80
    assert score_age(40, pref) == 60.0  # 40-32=8, 8*5=40, 100-40=60


def test_score_age_none():
    pref = UserPreference(min_age=22, max_age=32)
    assert score_age(None, pref) == 50.0


def test_score_height_perfect():
    pref = UserPreference(min_height=160, max_height=185)
    assert score_height(175, pref) == 100.0


def test_score_height_outside():
    pref = UserPreference(min_height=160, max_height=185)
    assert score_height(150, pref) == 80.0  # 160-150=10, 10*2=20
    assert score_height(200, pref) == 70.0  # 200-185=15, 15*2=30


def test_score_education_meets():
    pref = UserPreference(education_level=2)  # 大专
    assert score_education(3, pref) == 100.0  # 本科 >= 大专


def test_score_education_below():
    pref = UserPreference(education_level=3)  # 本科
    assert score_education(2, pref) == 75.0  # 大专 < 本科, diff=1, 1*25=25


def test_score_education_no_pref():
    pref = UserPreference(education_level=0)
    assert score_education(1, pref) == 100.0


def test_score_income_meets():
    pref = UserPreference(income_min=3)  # 10K+
    assert score_income(4, pref) == 100.0


def test_score_income_below():
    pref = UserPreference(income_min=3)  # 10K+
    assert score_income(1, pref) == 60.0  # diff=2, 2*20=40


def test_score_city_match():
    pref = UserPreference(city_ids='[1, 2]')
    assert score_city(1, pref) == 100.0


def test_score_city_no_match():
    pref = UserPreference(city_ids='[1, 2]')
    assert score_city(99, pref) == 0.0


def test_score_city_no_pref():
    pref = UserPreference(city_ids=None)
    assert score_city(99, pref) == 100.0


def test_score_tags_perfect():
    pref = UserPreference(tags='["旅行", "音乐"]')
    assert score_tags(["旅行", "音乐"], pref) == 100.0


def test_score_tags_partial():
    pref = UserPreference(tags='["旅行", "音乐"]')
    # Jaccard: common=1 (旅行), union=3 (旅行,音乐,摄影) => 1/3
    assert score_tags(["旅行", "摄影"], pref) == pytest.approx(33.33, 0.1)


def test_score_tags_no_overlap():
    pref = UserPreference(tags='["旅行", "音乐"]')
    assert score_tags(["游戏", "动漫"], pref) == 0.0


# ---------------------------------------------------------------------------
# Integration tests for compute_match_score
# ---------------------------------------------------------------------------
def test_compute_match_score_perfect_match(db, sample_user, target_user):
    """目标用户完美匹配偏好，分数应该很高。"""
    pref = db.query(UserPreference).filter(UserPreference.user_id == sample_user.id).first()
    profile = db.query(UserProfile).filter(UserProfile.user_id == target_user.id).first()

    score, reason = compute_match_score(target_user, profile, pref)

    assert score >= 80.0
    assert score <= 100.0
    assert reason is not None
    # 解析 reason JSON
    reasons = json.loads(reason)
    assert "total" in reasons
    assert reasons["total"] == pytest.approx(score, 0.1)


def test_compute_match_score_poor_match(db, sample_user, mismatched_user):
    """目标用户不匹配偏好，分数应该很低。"""
    pref = db.query(UserPreference).filter(UserPreference.user_id == sample_user.id).first()
    profile = db.query(UserProfile).filter(UserProfile.user_id == mismatched_user.id).first()

    score, reason = compute_match_score(mismatched_user, profile, pref)

    assert score < 60.0
    assert reason is not None


def test_compute_match_score_no_profile(db, sample_user):
    """目标用户没有资料，分数应该适中偏低。"""
    user = User(
        email=_make_unique_email("noprofile"),
        nickname="NoProfile",
        gender=2,
        birthday=date(1995, 1, 1),
        city_id=1,
        status=1,
    )
    db.add(user)
    db.commit()

    pref = db.query(UserPreference).filter(UserPreference.user_id == sample_user.id).first()
    score, reason = compute_match_score(user, None, pref)

    # 没有资料时，很多维度给 50 分，总分应该在 50-70 之间
    assert 30.0 <= score <= 70.0


# ---------------------------------------------------------------------------
# Bidirectional score tests
# ---------------------------------------------------------------------------
def test_compute_bidirectional_score(db, sample_user, target_user):
    """双向匹配分数应该是两个方向分数的平均。"""
    # 为目标用户创建偏好
    pref_target = UserPreference(
        user_id=target_user.id,
        min_age=25,
        max_age=35,
        min_height=170,
        max_height=190,
        education_level=2,
        income_min=2,
        city_ids=json.dumps([1]),
        tags=json.dumps(["旅行", "美食"]),
    )
    db.add(pref_target)
    db.commit()

    pref_sample = db.query(UserPreference).filter(UserPreference.user_id == sample_user.id).first()
    profile_sample = db.query(UserProfile).filter(UserProfile.user_id == sample_user.id).first()
    profile_target = db.query(UserProfile).filter(UserProfile.user_id == target_user.id).first()

    score, reason = compute_bidirectional_score(
        sample_user, profile_sample, pref_sample,
        target_user, profile_target, pref_target,
    )

    assert 0.0 <= score <= 100.0
    reasons = json.loads(reason)
    assert "bidirectional_score" in reasons
    assert "user_a_to_b" in reasons
    assert "user_b_to_a" in reasons


# ---------------------------------------------------------------------------
# Recommendation engine tests
# ---------------------------------------------------------------------------
def test_get_recommended_users_basic(db, sample_user, target_user, mismatched_user):
    """推荐系统应该返回按匹配分数排序的用户。"""
    users, total = get_recommended_users(db, sample_user, limit=20, offset=0)

    assert total >= 2  # target + mismatch
    assert len(users) >= 2

    # 第一个应该是匹配分数最高的
    scores = [u["match_score"] for u in users]
    assert scores == sorted(scores, reverse=True)

    # target_user 应该排在 mismatched_user 前面（如果两者都在结果中）
    nicknames = [u["nickname"] for u in users]
    if "Target" in nicknames and "Mismatch" in nicknames:
        target_idx = nicknames.index("Target")
        mismatch_idx = nicknames.index("Mismatch")
        assert target_idx < mismatch_idx


def test_get_recommended_users_pagination(db, sample_user, target_user, mismatched_user):
    """分页应该正常工作。"""
    users_page1, total = get_recommended_users(db, sample_user, limit=1, offset=0)
    users_page2, _ = get_recommended_users(db, sample_user, limit=1, offset=1)

    assert len(users_page1) == 1
    assert len(users_page2) == 1
    assert users_page1[0]["id"] != users_page2[0]["id"]
    assert total >= 2


def test_get_recommended_users_min_score(db, sample_user, target_user, mismatched_user):
    """最低分数过滤应该排除低分用户。"""
    users, total = get_recommended_users(db, sample_user, min_score=70.0)

    for u in users:
        assert u["match_score"] >= 70.0


def test_get_recommended_users_exclude_liked(db, sample_user, target_user, client):
    """已喜欢的用户应该被排除。"""
    from app.db.models import Match

    # 创建喜欢记录
    match = Match(
        user_a_id=sample_user.id,
        user_b_id=target_user.id,
        status=0,
        match_score=0.0,
    )
    db.add(match)
    db.commit()

    users, total = get_recommended_users(db, sample_user, exclude_liked=True)
    ids = [u["id"] for u in users]
    assert target_user.id not in ids


def test_get_recommended_users_gender_filter(db, sample_user, target_user):
    """性别过滤应该只返回异性用户。"""
    users, total = get_recommended_users(db, sample_user, gender_filter=True)

    for u in users:
        # sample_user is male (gender=1), so targets should be female (gender=2)
        assert u["gender"] == 2


def test_get_recommended_users_fields(db, sample_user, target_user):
    """返回的用户字典应该包含所有预期字段。"""
    users, total = get_recommended_users(db, sample_user, limit=1)

    u = users[0]
    assert "id" in u
    assert "nickname" in u
    assert "avatar_url" in u
    assert "gender" in u
    assert "age" in u
    assert "city_id" in u
    assert "bio" in u
    assert "tags" in u
    assert "height" in u
    assert "education" in u
    assert "income_level" in u
    assert "match_score" in u
    assert "match_reason" in u


# ---------------------------------------------------------------------------
# API integration tests
# ---------------------------------------------------------------------------
def test_discover_returns_scores(client, auth_headers, db):
    """发现页 API 应该返回包含匹配分数的用户列表。"""
    # 创建多个候选用户
    for i in range(3):
        user = User(
            email=_make_unique_email(f"discover{i}"),
            nickname=f"Discover{i}",
            gender=2,
            birthday=date(1995, 1, 1),
            city_id=1,
            status=1,
        )
        db.add(user)
        db.flush()
        profile = UserProfile(
            user_id=user.id,
            height=160 + i * 10,
            education=2 + i,
            income_level=2 + i,
            tags=json.dumps(["旅行"] if i == 0 else ["游戏"]),
        )
        db.add(profile)
    db.commit()

    r = client.get("/api/v1/users/discover", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()

    assert "users" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data

    for u in data["users"]:
        assert "match_score" in u
        assert "match_reason" in u


def test_discover_pagination(client, auth_headers, db):
    """发现页分页参数应该生效。"""
    # 创建多个候选用户
    for i in range(5):
        user = User(
            email=_make_unique_email(f"page{i}"),
            nickname=f"Page{i}",
            gender=2,
            birthday=date(1995, 1, 1),
            city_id=1,
            status=1,
        )
        db.add(user)
    db.commit()

    r = client.get("/api/v1/users/discover?limit=2&offset=0", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["limit"] == 2
    assert data["offset"] == 0
    # 实际返回数量取决于数据库中符合条件的异性用户数
    assert len(data["users"]) <= 2


def test_discover_min_score_filter(client, auth_headers, db):
    """最低匹配分数过滤应该生效。"""
    # 创建两个用户：一个高分，一个低分
    high_user = User(
        email=_make_unique_email("high"),
        nickname="HighScore",
        gender=2,
        birthday=date(1995, 1, 1),
        city_id=1,
        status=1,
    )
    db.add(high_user)
    db.flush()
    high_profile = UserProfile(
        user_id=high_user.id,
        height=170,
        education=3,
        income_level=3,
        tags=json.dumps(["旅行", "音乐"]),
    )
    db.add(high_profile)

    low_user = User(
        email=_make_unique_email("low"),
        nickname="LowScore",
        gender=2,
        birthday=date(2005, 1, 1),
        city_id=99,
        status=1,
    )
    db.add(low_user)
    db.flush()
    low_profile = UserProfile(
        user_id=low_user.id,
        height=140,
        education=1,
        income_level=1,
        tags=json.dumps(["游戏"]),
    )
    db.add(low_profile)
    db.commit()

    r = client.get("/api/v1/users/discover?min_score=70", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()

    for u in data["users"]:
        assert u["match_score"] >= 70.0


def test_like_creates_match_with_score(client, auth_headers, user_b, db):
    """互相喜欢时应该计算匹配分数。"""
    # 从 JWT token 中提取 user id
    from jose import jwt
    from app.core.config import settings

    token_a = auth_headers["Authorization"].replace("Bearer ", "")
    token_b = user_b["Authorization"].replace("Bearer ", "")
    payload_a = jwt.decode(token_a, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    payload_b = jwt.decode(token_b, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    user_a_id = int(payload_a["sub"])
    user_b_id = int(payload_b["sub"])

    # 确保两个用户不同
    assert user_a_id != user_b_id

    # A likes B
    r = client.post("/api/v1/matches/like", json={"to_user_id": user_b_id}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["matched"] is False

    # B likes A => mutual match
    r = client.post("/api/v1/matches/like", json={"to_user_id": user_a_id}, headers=user_b)
    assert r.status_code == 200
    assert r.json()["matched"] is True

    # 检查匹配记录是否有分数（需要刷新 db session 以获取最新数据）
    from app.db.models import Match
    db.expire_all()
    match = db.query(Match).filter(
        ((Match.user_a_id == user_a_id) & (Match.user_b_id == user_b_id)) |
        ((Match.user_a_id == user_b_id) & (Match.user_b_id == user_a_id))
    ).first()

    assert match is not None
    assert match.match_score is not None
    assert float(match.match_score) > 0.0
    assert match.match_reason is not None
