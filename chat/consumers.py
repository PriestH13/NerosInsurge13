import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GlobalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('global_chat', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('global_chat', self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')

        await self.channel_layer.group_send(
            'global_chat',
            {
                'type': 'chat_message',
                'message': message,
                'username': self.scope['user'].username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
        }))
