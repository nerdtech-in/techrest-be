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
        
class TableStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.franchise = self.scope['url_route']['kwargs']['franchise']
        self.outlet = self.scope['url_route']['kwargs']['outlet']
        self.room_group_name = f'tables_{self.franchise}_{self.outlet}'
        
        print(self.room_group_name)  # Add this line to print the channel name
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Handle disconnection
        pass

    async def send_table_status(self, event):
        tables = Table.objects.all()
        table_data = [{'id': table.id, 'table_color': table.get_color()} for table in tables]
        await self.send(text_data=json.dumps({'tables': table_data}))

    async def update_table_color(self, event):
        table_id = event['table_id']
        table_color = event['table_color']
        await self.send(text_data=json.dumps({'table_id': table_id, 'table_color': table_color}))
