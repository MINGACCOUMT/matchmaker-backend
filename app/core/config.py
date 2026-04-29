"""
核心配置模块
"""
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    APP_NAME: str = "Matchmaker Backend"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # API 配置
    API_V1_PREFIX: str = "/api/v1"

    # 数据库配置（从环境变量读取，默认 MySQL 本地开发）
    DATABASE_URL: str = "mysql+pymysql://matchmaker:matchmaker_pass_2024@localhost:3306/matchmaker"

    # JWT 配置
    SECRET_KEY: str = "matchmaker-jwt-secret-2024-development"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 天

    # CORS 配置（生产环境）
    # 支持多种格式：["*"]、"*"、"*"
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> List[str]:
        """解析 CORS 来源列表"""
        if self.BACKEND_CORS_ORIGINS == "*":
            return ["*"]
        try:
            # 尝试解析为 JSON 数组
            return json.loads(self.BACKEND_CORS_ORIGINS)
        except:
            # 如果不是 JSON，按逗号分隔
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]

    # Supabase 配置
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
