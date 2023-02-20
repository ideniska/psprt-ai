from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.conf import settings


class ProgressBarConsumer(AsyncJsonWebsocketConsumer):
    async def celery_task_update(self, event):
        message = event["data"]
        print(f"{message=}")
        await self.send_json(message)

    async def connect(self):
        print("connect")
        await self.accept()
        session_key = self.scope["cookies"][settings.SESSION_COOKIE_NAME]
        await self.channel_layer.group_add(
            session_key, self.channel_name
        )  # get or create a group with name session_key and use current channel_name for connection

    async def receive_json(self, content: dict, **kwargs):
        print(f"{content=}")
        # await self.send_json(content)

    async def disconnect(self, close_code):
        print("disconnect")
        # await self.close()
