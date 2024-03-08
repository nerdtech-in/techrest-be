# consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class FranchiseOutletConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.franchise = self.scope['url_route']['kwargs']['franchise']
        self.outlet = self.scope['url_route']['kwargs']['outlet']
        self.room_group_name = f'{self.franchise}_{self.outlet}'
        print(self.room_group_name)
        
        # Join the room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        order = text_data_json['order']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'order_details',
                'order': order
            }
        )
    
    async def order_details(self, event):
        order = event['order']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'order': order
        }))