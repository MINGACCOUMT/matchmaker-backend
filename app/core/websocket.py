"""
WebSocket 连接管理器
"""
from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 存储所有活跃连接: {user_id: WebSocket}
        self.active_connections: Dict[int, WebSocket] = {}
        # 存储聊天室连接: {chat_id: [user_id, user_id, ...]}
        self.chat_rooms: Dict[int, List[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """连接用户"""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        """断开用户连接"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            # 从所有聊天室移除该用户
            for chat_id in self.chat_rooms:
                if user_id in self.chat_rooms[chat_id]:
                    self.chat_rooms[chat_id].remove(user_id)

    async def send_personal_message(self, message: dict, user_id: int):
        """发送个人消息"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(user_id)

    async def broadcast_to_chat(self, message: dict, chat_id: int, exclude_user_id: int = None):
        """向聊天室广播消息"""
        if chat_id in self.chat_rooms:
            for user_id in self.chat_rooms[chat_id]:
                if exclude_user_id and user_id == exclude_user_id:
                    continue
                await self.send_personal_message(message, user_id)

    def join_chat_room(self, user_id: int, chat_id: int):
        """加入聊天室"""
        if chat_id not in self.chat_rooms:
            self.chat_rooms[chat_id] = []
        if user_id not in self.chat_rooms[chat_id]:
            self.chat_rooms[chat_id].append(user_id)

    def leave_chat_room(self, user_id: int, chat_id: int):
        """离开聊天室"""
        if chat_id in self.chat_rooms and user_id in self.chat_rooms[chat_id]:
            self.chat_rooms[chat_id].remove(user_id)

    def is_user_online(self, user_id: int) -> bool:
        """检查用户是否在线"""
        return user_id in self.active_connections

    def get_online_users_in_chat(self, chat_id: int) -> List[int]:
        """获取聊天室中的在线用户"""
        if chat_id not in self.chat_rooms:
            return []
        return [uid for uid in self.chat_rooms[chat_id] if self.is_user_online(uid)]


# 全局连接管理器实例
manager = ConnectionManager()
