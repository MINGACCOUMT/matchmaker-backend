"""
数据库连接配置
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 本地开发使用 SQLite，生产环境使用 PostgreSQL
if settings.ENVIRONMENT == "development" and settings.DATABASE_URL.startswith("postgresql"):
    # 本地开发降级到 SQLite
    db_path = "./matchmaker_dev.db"
    DATABASE_URL = f"sqlite:///{db_path}"
else:
    DATABASE_URL = settings.DATABASE_URL

# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

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
