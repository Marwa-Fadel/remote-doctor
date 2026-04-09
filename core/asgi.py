import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import notifications.routing # <-- سيتم إنشاء هذا الملف في الخطوات التالية

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# هذا هو الموجه الرئيسي للمشروع
application = ProtocolTypeRouter({
    # طلبات HTTP العادية ستذهب إلى Django كالمعتاد
    "http": get_asgi_application(),
    
    # طلبات WebSocket سيتم توجيهها إلى نظام Channels
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notifications.routing.websocket_urlpatterns
        )
    ),
})
