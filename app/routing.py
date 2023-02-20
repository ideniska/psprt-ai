from django.urls import path, include
from .consumers import ProgressBarConsumer

websocket_urlpatterns = [
    path("ws/progress/", ProgressBarConsumer.as_asgi()),
]
