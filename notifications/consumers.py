import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        """يتم استدعاؤها عند محاولة العميل فتح اتصال."""
        user = self.scope['user']

        if not user.is_authenticated:
            await self.close() 
        else:
            self.room_group_name = f'notifications_{user.id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept() 

    async def disconnect(self, close_code):
        """يتم استدعاؤها عند إغلاق الاتصال."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        """هذه الدالة تستقبل الرسائل من الخادم وترسلها إلى العميل."""
        message = event['message']
        await self.send(text_data=json.dumps(message))
