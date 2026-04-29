"""
图片上传 API
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, UserProfile
from app.core.auth import get_current_user
import os
from datetime import datetime
import uuid

router = APIRouter()

# 文件上传目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 允许的文件类型
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
# 最大文件大小（10MB）
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_file(file: UploadFile) -> tuple[bool, str]:
    """验证文件"""
    # 检查文件扩展名
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"不支持的文件类型：{ext}"
    
    # 检查文件大小
    file.file.seek(0, 2)  # 跳到文件末尾
    file_size = int(file.file.tell())
    file.file.seek(0)  # 回到文件开头
    
    if file_size > MAX_FILE_SIZE:
        return False, f"文件太大：{file_size / 1024 / 1024:.2f}MB，最大允许 10MB"
    
    return True, "文件验证通过"


@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传头像
    """
    # 验证文件
    is_valid, message = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1]
    filename = f"{user.id}_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败：{str(e)}")
    
    # 生成文件 URL
    file_url = f"/uploads/{filename}"
    
    # 更新用户头像
    user.avatar_url = file_url
    db.commit()
    db.refresh(user)
    
    return {
        "message": "头像上传成功",
        "file_url": file_url,
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url,
        }
    }


@router.post("/upload-gallery")
async def upload_gallery(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传相册图片
    """
    # 验证文件
    is_valid, message = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1]
    filename = f"gallery_{user.id}_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败：{str(e)}")
    
    # 生成文件 URL
    file_url = f"/uploads/{filename}"
    
    return {
        "message": "相册图片上传成功",
        "file_url": file_url,
        "filename": filename,
        "uploaded_at": datetime.utcnow().isoformat()
    }


@router.delete("/gallery/{filename}")
async def delete_gallery_image(
    filename: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除相册图片
    """
    # 验证文件名格式
    if not filename.startswith(f"gallery_{user.id}_"):
        raise HTTPException(status_code=403, detail="无权删除此文件")
    
    # 删除文件
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": "图片删除成功"}
    else:
        raise HTTPException(status_code=404, detail="文件不存在")


@router.get("/gallery")
async def get_gallery_images(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户相册图片列表
    """
    # 获取所有相册图片
    gallery_images = []
    
    for filename in os.listdir(UPLOAD_DIR):
        if filename.startswith(f"gallery_{user.id}_"):
            file_path = os.path.join(UPLOAD_DIR, filename)
            file_stat = os.stat(file_path)
            
            gallery_images.append({
                "filename": filename,
                "file_url": f"/uploads/{filename}",
                "size": file_stat.st_size,
                "created_at": datetime.fromtimestamp(file_stat.st_ctime).isoformat()
            })
    
    # 按创建时间排序
    gallery_images.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "images": gallery_images,
        "count": len(gallery_images)
    }


@router.post("/set-avatar")
async def set_avatar(
    filename: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    设置用户头像（从相册中选择）
    """
    # 验证文件名格式
    if not filename.startswith(f"gallery_{user.id}_"):
        raise HTTPException(status_code=403, detail="无权使用此文件")
    
    # 检查文件是否存在
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 生成文件 URL
    file_url = f"/uploads/{filename}"
    
    # 更新用户头像
    user.avatar_url = file_url
    db.commit()
    db.refresh(user)
    
    return {
        "message": "头像设置成功",
        "file_url": file_url,
        "user": {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "avatar_url": user.avatar_url,
        }
    }
