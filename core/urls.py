from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/users/', include('users.urls')),
    path('api/cases/', include('cases.urls')),
    path('api/responses/', include('responses.urls')),
    path('api/guides/', include('emergency.urls')),
    path('api/notifications/', include('notifications.urls')),

    # GET /api/schema/ -> يقوم بتنزيل ملف التوثيق (yaml)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # GET /api/docs/ -> يعرض واجهة Swagger التفاعلية (موصى به)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # GET /api/redoc/ -> يعرض واجهة ReDoc (شكل آخر للتوثيق)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
