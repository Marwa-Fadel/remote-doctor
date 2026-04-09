from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer
from drf_spectacular.utils import extend_schema 

class NotificationListView(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class MarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: {"description": "Marked as read"}}
    )
    def post(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, user=request.user)
        if not notification.is_read:
            notification.is_read = True
            notification.save()
        return Response({"message": "Marked as read"}, status=status.HTTP_200_OK)
