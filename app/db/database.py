"""
数据库连接配置
"""
from sqlalchemy import create_engine, URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 本地开发使用 SQLite，生产环境使用 PostgreSQL
if settings.ENVIRONMENT == "development" and (not settings.DATABASE_URL or settings.DATABASE_URL == ""):
    # 本地开发使用 SQLite
    db_path = "./matchmaker_dev.db"
    DATABASE_URL = f"sqlite:///{db_path}"
else:
    DATABASE_URL = settings.DATABASE_URL

# 创建数据库引擎
# 对于 PostgreSQL，强制使用 IPv4（避免 IPv6 连接问题）
if DATABASE_URL.startswith("postgresql"):
    # 替换主机名为 IPv4 地址（如果有）
    # 或者使用连接池配置
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000"
        }
    )
elif DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
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
