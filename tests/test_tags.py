"""
标签管理 API 测试
"""
import json
import pytest

from conftest import TestingSessionLocal
from app.db.models import User, UserProfile


def _make_unique_email():
    import uuid
    return f"tagtest_{uuid.uuid4().hex[:8]}@example.com"


def _create_user_and_login(client, email: str, password: str = "testpass123"):
    """注册用户并返回 JWT token。"""
    # 注册
    resp = client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "nickname": "TagTester",
        "gender": 1,
        "tags": json.dumps(["运动", "音乐"]),
    })
    assert resp.status_code == 200, f"Register failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestSystemTags:
    """系统标签接口测试"""

    def test_get_system_tags(self, client):
        resp = client.get("/api/v1/tags/system")
        assert resp.status_code == 200
        data = resp.json()
        assert "tags" in data
        assert "popular" in data
        assert isinstance(data["tags"], list)
        assert isinstance(data["popular"], list)
        assert len(data["tags"]) > 0
        assert "旅行" in data["tags"]
        assert "美食" in data["popular"]


class TestMyTags:
    """用户标签 CRUD 测试"""

    def test_get_my_tags_empty(self, client):
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        # 新用户默认没有标签（因为注册时 tags 被 parse_tags 处理）
        resp = client.get("/api/v1/tags/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "tags" in data
        assert isinstance(data["tags"], list)

    def test_update_my_tags(self, client):
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        # 覆盖更新标签
        resp = client.put("/api/v1/tags/me", headers=headers, json={
            "tags": ["摄影", "旅行", "美食"]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["tags"] == ["摄影", "旅行", "美食"]
        # 验证数据库中存储的是 JSON 字符串
        db = TestingSessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            assert profile is not None
            stored = json.loads(profile.tags)
            assert stored == ["摄影", "旅行", "美食"]
        finally:
            db.close()

    def test_update_my_tags_deduplication(self, client):
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        resp = client.put("/api/v1/tags/me", headers=headers, json={
            "tags": ["摄影", "摄影", "旅行", "旅行", "美食"]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["tags"] == ["摄影", "旅行", "美食"]

    def test_update_my_tags_limit_20(self, client):
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        resp = client.put("/api/v1/tags/me", headers=headers, json={
            "tags": [f"tag{i}" for i in range(25)]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["tags"]) == 20

    def test_update_my_tags_max_length(self, client):
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        resp = client.put("/api/v1/tags/me", headers=headers, json={
            "tags": ["a" * 21, "正常标签"]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "a" * 21 not in data["tags"]
        assert "正常标签" in data["tags"]

    def test_add_my_tag(self, client):
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        # 先设置初始标签
        client.put("/api/v1/tags/me", headers=headers, json={"tags": ["运动"]})
        # 添加新标签
        resp = client.post("/api/v1/tags/me", headers=headers, json={"tag": "音乐"})
        assert resp.status_code == 200
        data = resp.json()
        assert "音乐" in data["tags"]
        assert "运动" in data["tags"]

    def test_add_duplicate_tag(self, client):
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        client.put("/api/v1/tags/me", headers=headers, json={"tags": ["运动"]})
        resp = client.post("/api/v1/tags/me", headers=headers, json={"tag": "运动"})
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]

    def test_add_tag_too_long(self, client):
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        resp = client.post("/api/v1/tags/me", headers=headers, json={"tag": "a" * 21})
        assert resp.status_code == 422

    def test_add_tag_empty(self, client):
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        resp = client.post("/api/v1/tags/me", headers=headers, json={"tag": "   "})
        assert resp.status_code == 422

    def test_add_tag_max_20(self, client):
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        client.put("/api/v1/tags/me", headers=headers, json={"tags": [f"tag{i}" for i in range(20)]})
        resp = client.post("/api/v1/tags/me", headers=headers, json={"tag": "额外标签"})
        assert resp.status_code == 422
        assert "Max 20 tags" in resp.json()["detail"]

    def test_delete_my_tag(self, client):
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        client.put("/api/v1/tags/me", headers=headers, json={"tags": ["运动", "音乐", "摄影"]})
        resp = client.delete("/api/v1/tags/me/音乐", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "音乐" not in data["tags"]
        assert "运动" in data["tags"]
        assert "摄影" in data["tags"]

    def test_delete_nonexistent_tag(self, client):
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        client.put("/api/v1/tags/me", headers=headers, json={"tags": ["运动"]})
        resp = client.delete("/api/v1/tags/me/不存在的标签", headers=headers)
        assert resp.status_code == 404

    def test_delete_tag_no_profile(self, client):
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        # 手动删除 profile
        db = TestingSessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            if profile:
                db.delete(profile)
                db.commit()
        finally:
            db.close()
        resp = client.delete("/api/v1/tags/me/运动", headers=headers)
        assert resp.status_code == 404


class TestTagsIntegration:
    """标签功能集成测试"""

    def test_users_me_returns_parsed_tags(self, client):
        """验证 /users/me 正确返回解析后的标签列表"""
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        client.put("/api/v1/tags/me", headers=headers, json={"tags": ["编程", "AI", "开源"]})
        resp = client.get("/api/v1/users/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "profile" in data
        assert data["profile"]["tags"] == ["编程", "AI", "开源"]

    def test_users_me_update_tags(self, client):
        """验证通过 /users/me 更新标签也正确序列化"""
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        resp = client.put("/api/v1/users/me", headers=headers, json={
            "tags": json.dumps(["旅行", "摄影"])
        })
        assert resp.status_code == 200
        # 验证读取时正确解析
        resp = client.get("/api/v1/users/me", headers=headers)
        data = resp.json()
        assert data["profile"]["tags"] == ["旅行", "摄影"]

    def test_tags_persisted_as_json_string(self, client):
        """验证数据库中 tags 存储为 JSON 字符串"""
        email = _make_unique_email()
        headers = _create_user_and_login(client, email)
        client.put("/api/v1/tags/me", headers=headers, json={"tags": ["测试", "验证"]})
        db = TestingSessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            assert profile.tags is not None
            # 应该能成功解析为 JSON
            parsed = json.loads(profile.tags)
            assert parsed == ["测试", "验证"]
        finally:
            db.close()
