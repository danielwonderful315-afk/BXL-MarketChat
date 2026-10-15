import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    """One consumer instance per open WebSocket connection to a conversation room."""

    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data["message"]
        user = self.scope["user"]

        message = await self.save_message(user, message_text)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_text,
                "sender": user.username,
                "sender_id": user.id,
                "timestamp": message.created_at.isoformat(),
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, user, text):
        conversation = Conversation.objects.get(pk=self.conversation_id)
        return Message.objects.create(conversation=conversation, sender=user, content=text)
