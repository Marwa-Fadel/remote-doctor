from django.urls import path
from .views import NotificationListView, MarkAsReadView

urlpatterns = [
    # GET /api/notifications/ -> لعرض كل الإشعارات
    path('', NotificationListView.as_view(), name='notification-list'),
    
    # POST /api/notifications/123/read/ -> لتحديد الإشعار رقم 123 كمقروء
    path('<int:pk>/read/', MarkAsReadView.as_view(), name='notification-mark-read'),
]
