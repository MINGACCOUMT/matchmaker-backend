"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="相亲网站后端 API - 支持 WebSocket 实时聊天",
    docs_url="/docs",
    redoc_url="/redoc",
)


# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
    }


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Matchmaker Backend API",
        "version": settings.VERSION,
        "docs": "/docs",
        "websocket": "WebSocket 实时聊天已启用",
    }


# API 路由
from app.api.endpoints import auth, chat
from app.api.v1.endpoints import users, matches, websocket

# 认证 API（v1 版本也复制了一份）
app.include_router(auth.router, prefix="/api/auth")

# 聊天 API（使用旧版本）
app.include_router(chat.router, prefix="/api/chat")

# 用户 API（v1 版本）
app.include_router(users.router, prefix="/api/v1")

# 匹配 API（v1 版本）
app.include_router(matches.router, prefix="/api/v1")

# WebSocket API
app.include_router(websocket.router, prefix="/api")


# 启动时自动创建数据库表
@app.on_event("startup")
def on_startup():
    try:
        from app.db.database import engine
        from app.db.models import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
        print("✅ WebSocket 实时聊天已启用")
    except Exception as e:
        print(f"Database connection failed (app will continue): {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
