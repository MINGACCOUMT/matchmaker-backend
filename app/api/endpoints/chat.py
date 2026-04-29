"""
聊天相关 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Chat, Message
from app.schemas import ConversationsResponse, MessagesResponse, SendMessageRequest
from app.core.auth import get_current_user
from datetime import datetime

router = APIRouter()


@router.get("/conversations")
def get_conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chats = db.query(Chat).filter(
        ((Chat.user_a_id == user.id) | (Chat.user_b_id == user.id)) & (Chat.is_active == True)
    ).order_by(Chat.last_message_at.desc()).all()

    conversations = []
    for chat in chats:
        other_id = chat.user_b_id if chat.user_a_id == user.id else chat.user_a_id
        other = db.query(User).filter(User.id == other_id).first()
        last_msg = db.query(Message).filter(Message.chat_id == chat.id).order_by(Message.created_at.desc()).first()
        unread = db.query(Message).filter(
            Message.chat_id == chat.id,
            Message.sender_id != user.id,
            Message.is_read == False
        ).count()

        conversations.append({
            "id": chat.id,
            "match_id": chat.match_id,
            "other_user": {
                "id": other.id if other else other_id,
                "nickname": other.nickname if other else "未知用户",
                "avatar_url": other.avatar_url if other else None,
            },
            "last_message": last_msg.content if last_msg else None,
            "last_message_at": chat.last_message_at,
            "unread_count": unread,
        })

    return {"conversations": conversations}


@router.get("/messages/{conv_id}")
def get_messages(conv_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == conv_id).first()
    if not chat or (chat.user_a_id != user.id and chat.user_b_id != user.id):
        return {"messages": []}

    messages = db.query(Message).filter(Message.chat_id == conv_id).order_by(Message.created_at.asc()).all()
    return {
        "messages": [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "content": m.content,
                "created_at": m.created_at,
                "is_read": m.is_read,
            }
            for m in messages
        ]
    }


@router.post("/messages")
def send_message(req: SendMessageRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv_id = int(req.conversation_id)
    chat = db.query(Chat).filter(Chat.id == conv_id).first()
    if not chat or (chat.user_a_id != user.id and chat.user_b_id != user.id):
        return {"success": False, "error": "Chat not found"}

    msg = Message(
        chat_id=conv_id,
        sender_id=user.id,
        content=req.content,
        created_at=datetime.utcnow(),
    )
    db.add(msg)
    chat.last_message_at = datetime.utcnow()
    db.commit()
    db.refresh(msg)

    return {
        "success": True,
        "message": {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "content": msg.content,
            "created_at": msg.created_at,
            "is_read": msg.is_read,
        }
    }
