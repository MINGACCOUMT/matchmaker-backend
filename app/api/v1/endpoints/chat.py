"""
聊天相关 API 端点
"""
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.db.models import User, Chat, Message, Match, UserProfile
from app.schemas import ConversationsResponse, MessageOut, MessagesResponse, SendMessageRequest

router = APIRouter(prefix="/chat", tags=["chat"])


def get_conversation_details(chat: Chat, user_id: int, db: Session) -> dict:
    """获取会话详情"""
    other_id = chat.user_a_id if chat.user_a_id != user_id else chat.user_b_id
    other = db.query(User).filter(User.id == other_id).first()
    other_profile = db.query(UserProfile).filter(UserProfile.user_id == other_id).first()
    if not other:
        return None

    last_message = db.query(Message).filter(
        Message.chat_id == chat.id,
        Message.is_deleted == False
    ).order_by(Message.created_at.desc()).first()

    unread = db.query(Message).filter(
        Message.chat_id == chat.id,
        Message.sender_id != user_id,
        Message.is_read == False,
        Message.is_deleted == False
    ).count()

    return {
        "id": chat.id,
        "match_id": chat.match_id,
        "other_user": {
            "id": other.id,
            "nickname": other.nickname,
            "avatar_url": other.avatar_url,
        } if other else None,
        "last_message": last_message.content if last_message else None,
        "last_message_at": last_message.created_at.isoformat() if last_message else None,
        "unread_count": unread,
    }


@router.get("/conversations", response_model=ConversationsResponse)
def get_conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户的聊天会话列表"""
    chats = db.query(Chat).filter(
        (Chat.user_a_id == user.id) | (Chat.user_b_id == user.id),
        Chat.is_active == True
    ).order_by(Chat.last_message_at.desc().nullslast()).all()

    conversations = []
    for chat in chats:
        details = get_conversation_details(chat, user.id, db)
        if details:
            conversations.append(details)

    return {"conversations": conversations}


@router.get("/messages/{chat_id}", response_model=MessagesResponse)
def get_messages(chat_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取指定会话的消息历史"""
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    # 验证用户是否属于该会话
    if chat.user_a_id != user.id and chat.user_b_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not part of this conversation")

    messages = db.query(Message).filter(
        Message.chat_id == chat_id,
        Message.is_deleted == False
    ).order_by(Message.created_at.asc()).all()

    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "sender_id": msg.sender_id,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
            "is_read": msg.is_read,
            "has_media": bool(msg.media_url),
        })

    return {"messages": result}


@router.post("/send")
def send_message(req: SendMessageRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """发送消息"""
    # 查找会话
    chat = db.query(Chat).filter(Chat.id == req.conversation_id).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    # 验证用户是否属于该会话
    if chat.user_a_id != user.id and chat.user_b_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not part of this conversation")

    try:
        # 创建新消息
        message = Message(
            chat_id=req.conversation_id,
            sender_id=user.id,
            content=req.content,
            is_read=False,
            is_deleted=False,
            created_at=datetime.utcnow(),
        )
        db.add(message)
        db.flush()

        # 更新会话的最后消息时间
        chat.last_message_at = datetime.utcnow()
        db.commit()

        # 返回创建的消息
        db.refresh(message)
        return {
            "id": message.id,
            "chat_id": req.conversation_id,
            "sender_id": user.id,
            "content": req.content,
            "created_at": message.created_at.isoformat(),
        }

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send message") from exc
