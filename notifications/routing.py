from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # ws://your-domain/ws/notifications/
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
