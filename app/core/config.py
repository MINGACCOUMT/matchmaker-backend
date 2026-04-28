"""
核心配置模块
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    APP_NAME: str = "Matchmaker Backend"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # API 配置
    API_V1_PREFIX: str = "/api/v1"

    # 数据库配置（生产环境从 Supabase 读取）
    DATABASE_URL: str = "postgresql://postgres:L.am19961209..@db.lwormsunwjwlutwqnlnt.supabase.co:5432/postgres"

    # JWT 配置
    SECRET_KEY: str = "matchmaker-jwt-secret-2024-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 天

    # CORS 配置（生产环境）
    BACKEND_CORS_ORIGINS: list = [
        "https://matchmaker-api.onrender.com",
        "https://matchmaker-frontend.vercel.app",
        "https://lwormsunwjwlutwqnlnt.supabase.co",
    ]

    # Supabase 配置
    SUPABASE_URL: str = "https://lwormsunwjwlutwqnlnt.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx3b3Jtc3V3d2x1dHd3FubG50Iiwicm9zZSI6ImFub24iLCJpYXQiOjE3MzczNTEwMDQsInV4cCI6MjA1OTY5NzQwNH0.UEfFt0zoSlJ3Jm2GzDT6T-R10ZRMLaqypaDWFnwZPjU"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
