from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import EmergencyGuide
from .serializers import EmergencyGuideSerializer

class GuideListView(ListAPIView):
    """
    واجهة برمجية لعرض قائمة بكل إرشادات الطوارئ.
    يمكن لأي مستخدم مسجل الدخول الوصول إليها.
    """
    queryset = EmergencyGuide.objects.all()
    serializer_class = EmergencyGuideSerializer
    permission_classes = [IsAuthenticated]
