"""
OAuth2 第三方登录
支持 GitHub 和 Google，需在 .env 中配置 CLIENT_ID / CLIENT_SECRET
"""
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, get_password_hash
from app.core.config import settings
from app.db.database import get_db
from app.db.models import User, UserProfile

router = APIRouter(prefix="/oauth", tags=["oauth"])

# ---------------------------------------------------------------------------
# Provider configs
# ---------------------------------------------------------------------------

PROVIDERS = {
    "github": {
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "user_url": "https://api.github.com/user",
        "email_url": "https://api.github.com/user/emails",
        "scope": "user:email",
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
    },
    "google": {
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "user_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scope": "openid email profile",
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
    },
}


def _http():
    import httpx
    return httpx.Client(timeout=30)


def _get_or_create_user(db: Session, email: str, nickname: str, avatar_url: Optional[str], provider: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user

    # 创建新用户（随机密码，用户无法直接登录）
    from datetime import datetime
    user = User(
        email=email,
        password_hash=get_password_hash(secrets.token_urlsafe(32)),
        nickname=nickname or email.split("@")[0],
        avatar_url=avatar_url,
        gender=0,
        status=1,
        last_active_at=datetime.utcnow(),
    )
    db.add(user)
    db.flush()

    profile = UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()
    db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Step 1: 返回授权 URL
# ---------------------------------------------------------------------------

@router.get("/{provider}/authorize")
def oauth_authorize(provider: str):
    cfg = PROVIDERS.get(provider)
    if not cfg:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    if not cfg["client_id"]:
        raise HTTPException(status_code=500, detail=f"{provider} OAuth not configured")

    state = secrets.token_urlsafe(16)
    params = {
        "client_id": cfg["client_id"],
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
        "scope": cfg["scope"],
        "state": state,
        "response_type": "code",
    }
    if provider == "google":
        params["access_type"] = "offline"
        params["prompt"] = "consent"

    import urllib.parse
    qs = urllib.parse.urlencode(params)
    return {"authorization_url": f"{cfg['authorize_url']}?{qs}", "state": state}


# ---------------------------------------------------------------------------
# Step 2: 回调处理
# ---------------------------------------------------------------------------

@router.get("/{provider}/callback")
def oauth_callback(provider: str, code: str, state: str = "", db: Session = Depends(get_db)):
    cfg = PROVIDERS.get(provider)
    if not cfg:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    if not cfg["client_id"]:
        raise HTTPException(status_code=500, detail=f"{provider} OAuth not configured")

    # Exchange code for access token
    token_data = {
        "client_id": cfg["client_id"],
        "client_secret": cfg["client_secret"],
        "code": code,
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
    }
    if provider == "github":
        token_data["accept"] = "application/json"

    headers = {"Accept": "application/json"}
    with _http() as client:
        r = client.post(cfg["token_url"], data=token_data, headers=headers)
        r.raise_for_status()
        token_resp = r.json()

    access_token = token_resp.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to obtain access token")

    # Fetch user info
    auth_header = {"Authorization": f"Bearer {access_token}"}
    with _http() as client:
        r = client.get(cfg["user_url"], headers=auth_header)
        r.raise_for_status()
        user_info = r.json()

    # Normalize email / nickname / avatar
    email: Optional[str] = user_info.get("email")
    nickname = user_info.get("name") or user_info.get("login") or "OAuth User"
    avatar_url = user_info.get("avatar_url") or user_info.get("picture")

    # GitHub 可能隐藏邮箱，需另行获取
    if provider == "github" and not email:
        with _http() as client:
            r = client.get(cfg["email_url"], headers=auth_header)
            if r.status_code == 200:
                emails = r.json()
                primary = next((e for e in emails if e.get("primary")), None)
                email = primary["email"] if primary else (emails[0]["email"] if emails else None)

    if not email:
        raise HTTPException(status_code=400, detail="OAuth provider did not return email")

    # 查找或创建用户
    user = _get_or_create_user(db, email, nickname, avatar_url, provider)
    jwt = create_access_token({"sub": str(user.id)})

    return {
        "access_token": jwt,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url,
        },
    }
