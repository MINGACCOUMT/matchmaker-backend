"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import settings

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="相亲网站后端 API - 支持实时聊天、图片上传、滑卡功能",
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


# 静态文件服务（用于上传的图片）
import os
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "features": {
            "auth": True,
            "websocket": True,
            "upload": True,
            "swipe": True,
        }
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
        "upload": "图片上传已启用",
        "swipe": "滑卡功能已启用",
    }


# API 路由
from app.api.v1.endpoints import users, matches, auth, chat, websocket, oauth, tags
from app.api.endpoints import upload, swipe

# REST API
app.include_router(auth.router, prefix="/api/auth")
app.include_router(oauth.router, prefix="/api/auth")
app.include_router(chat.router, prefix="/api/chat")
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(matches.router, prefix=settings.API_V1_PREFIX)
app.include_router(tags.router, prefix=settings.API_V1_PREFIX)
app.include_router(upload.router, prefix=settings.API_V1_PREFIX)
app.include_router(swipe.router, prefix=settings.API_V1_PREFIX)

# WebSocket API
app.include_router(websocket.router, prefix="/api")


# 启动时自动创建数据库表和上传目录
@app.on_event("startup")
def on_startup():
    try:
        import os
        from app.db.database import engine
        from app.db.models import Base
        
        # 创建数据库表
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
        
        # 创建上传目录
        os.makedirs("uploads", exist_ok=True)
        print("✅ Upload directory created/verified")
        
        print("✅ WebSocket 实时聊天已启用")
        print("✅ 图片上传已启用")
        print("✅ 滑卡功能已启用")
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
