"""
数据库连接配置
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 本地开发使用 MySQL，生产环境使用 PostgreSQL
DATABASE_URL = settings.DATABASE_URL

# 创建数据库引擎
# 根据 URL 类型选择正确的驱动和配置
if DATABASE_URL.startswith("mysql"):
    # MySQL 配置
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=10,
        max_overflow=20,
        connect_args={
            "connect_timeout": 10,
            "charset": "utf8mb4"
        }
    )
elif DATABASE_URL.startswith("postgresql"):
    # PostgreSQL 配置
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=10,
        max_overflow=20,
        connect_args={
            "connect_timeout": 10,
        }
    )
elif DATABASE_URL.startswith("sqlite"):
    # SQLite 配置
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # 默认配置
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
