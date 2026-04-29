"""
WebSocket 聊天路由
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict
import json
from app.db.database import get_db
from app.db.models import User, Chat, Message
from app.core.websocket import manager
from app.core.auth import get_current_user_ws
from datetime import datetime

router = APIRouter()


@router.websocket("/ws/chat/{chat_id}")
async def websocket_chat(websocket: WebSocket, chat_id: int, token: str = Query(...)):
    """
    WebSocket 聊天端点
    用法: ws://localhost:8000/ws/chat/1?token=YOUR_JWT_TOKEN
    """
    try:
        # 验证用户
        user = await get_current_user_ws(token)
        if not user:
            await websocket.close(code=4001, reason="Invalid token")
            return

        # 验证聊天是否存在
        db: Session = next(get_db())
        chat = db.query(Chat).filter(
            Chat.id == chat_id,
            ((Chat.user_a_id == user.id) | (Chat.user_b_id == user.id)),
            Chat.is_active == True
        ).first()
        if not chat:
            await websocket.close(code=4002, reason="Chat not found")
            return

        # 连接 WebSocket
        await manager.connect(websocket, user.id)
        manager.join_chat_room(user.id, chat_id)

        # 获取其他用户 ID
        other_user_id = chat.user_b_id if chat.user_a_id == user.id else chat.user_a_id

        # 发送在线状态
        if manager.is_user_online(other_user_id):
            await manager.send_personal_message({
                "type": "user_online",
                "user_id": other_user_id,
                "timestamp": datetime.utcnow().isoformat()
            }, user.id)

        # 发送欢迎消息
        await manager.send_personal_message({
            "type": "connected",
            "chat_id": chat_id,
            "user_id": user.id,
            "timestamp": datetime.utcnow().isoformat()
        }, user.id)

        # 发送未读消息
        unread_messages = db.query(Message).filter(
            Message.chat_id == chat_id,
            Message.sender_id != user.id,
            Message.is_read == False
        ).order_by(Message.created_at.asc()).all()

        for msg in unread_messages:
            await manager.send_personal_message({
                "type": "message",
                "id": msg.id,
                "chat_id": msg.chat_id,
                "sender_id": msg.sender_id,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "is_read": msg.is_read,
            }, user.id)

        # 标记未读消息为已读
        db.query(Message).filter(
            Message.chat_id == chat_id,
            Message.sender_id != user.id,
            Message.is_read == False
        ).update({"is_read": True})
        db.commit()

        try:
            while True:
                # 接收消息
                data = await websocket.receive_json()

                # 处理不同类型的消息
                if data.get("type") == "message":
                    content = data.get("content", "").strip()
                    if not content:
                        continue

                    # 保存消息到数据库
                    msg = Message(
                        chat_id=chat_id,
                        sender_id=user.id,
                        content=content,
                        is_read=False,
                        created_at=datetime.utcnow()
                    )
                    db.add(msg)

                    # 更新聊天最后消息时间
                    chat.last_message_at = datetime.utcnow()
                    db.commit()
                    db.refresh(msg)

                    # 构建消息对象
                    message_data = {
                        "type": "message",
                        "id": msg.id,
                        "chat_id": msg.chat_id,
                        "sender_id": msg.sender_id,
                        "sender_name": user.nickname,
                        "content": msg.content,
                        "created_at": msg.created_at.isoformat(),
                        "is_read": msg.is_read,
                    }

                    # 发送给自己（确认）
                    await manager.send_personal_message(message_data, user.id)

                    # 发送给对方
                    await manager.send_personal_message(message_data, other_user_id)

                elif data.get("type") == "typing":
                    # 发送输入状态
                    await manager.send_personal_message({
                        "type": "typing",
                        "user_id": user.id,
                        "is_typing": data.get("is_typing", False),
                        "timestamp": datetime.utcnow().isoformat()
                    }, other_user_id)

                elif data.get("type") == "read":
                    # 标记消息已读
                    db.query(Message).filter(
                        Message.chat_id == chat_id,
                        Message.sender_id == user.id,
                        Message.is_read == False
                    ).update({"is_read": True})
                    db.commit()

        except WebSocketDisconnect:
            pass

        finally:
            # 断开连接
            manager.leave_chat_room(user.id, chat_id)
            manager.disconnect(user_id)

            # 通知对方用户离线
            if manager.is_user_online(other_user_id):
                await manager.send_personal_message({
                    "type": "user_offline",
                    "user_id": user.id,
                    "timestamp": datetime.utcnow().isoformat()
                }, other_user_id)

    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close(code=4000, reason="Internal server error")
        except:
            pass


@router.get("/ws/online/{user_id}")
async def check_user_online(user_id: int):
    """检查用户是否在线"""
    return {
        "online": manager.is_user_online(user_id)
    }


@router.get("/ws/online/chat/{chat_id}")
async def get_online_users_in_chat(chat_id: int):
    """获取聊天室中的在线用户"""
    online_users = manager.get_online_users_in_chat(chat_id)
    return {
        "chat_id": chat_id,
        "online_users": online_users,
        "count": len(online_users)
    }
