from app.service_v2 import PhotoPreparation
from core.celery import app
from channels.layers import get_channel_layer
import asyncio
from .models import UserFile
from asgiref.sync import async_to_sync
from time import sleep


@app.task
def process_photos(session_key, uploaded_files):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        session_key,
        {
            "type": "celery_task_update",
            "data": {
                "progress": 0.1,
                "event": "started",
            },
        },
    )
    user_files = UserFile.objects.filter(id__in=uploaded_files)
    for file in user_files:
        photo_size = file.prepared_for
        file_path = file.file.path
        file_id = file.id
    service = PhotoPreparation(
        photo_size,
        file_path,
        session_key,
        file_id,
    )
    service.make()

    async_to_sync(channel_layer.group_send)(
        session_key,
        {
            "type": "celery_task_update",
            "data": {
                "progress": 0.8,
                "event": "finished",
            },
        },
    )
