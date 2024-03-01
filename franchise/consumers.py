from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
import json


class AdminPanelConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("admin_panel_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("admin_panel_group", self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event))
        
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))