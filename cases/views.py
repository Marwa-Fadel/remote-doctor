from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_spectacular.utils import extend_schema 

from .models import Case
from .serializers import CaseCreateSerializer, CaseListSerializer
from .utils import calculate_priority, auto_assign_doctor, match_doctor_specialty
from .permissions import IsDoctor
from emergency.models import EmergencyGuide
from responses.models import Response as CaseResponse
from notifications.models import Notification
from users.models import DoctorProfile
from .tasks import compress_case_image 

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notifications.serializers import NotificationSerializer

class CreateCaseView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CaseCreateSerializer, responses={201: None})
    def post(self, request):
        offline_id = request.data.get("offline_id")
        if offline_id and Case.objects.filter(offline_id=offline_id).exists():
            existing = Case.objects.get(offline_id=offline_id)
            return Response({"message": "Already synced", "case_id": existing.id}, status=200)

        serializer = CaseCreateSerializer(data=request.data)
        if serializer.is_valid():
            case = serializer.save(created_by=request.user, offline_id=offline_id)
            
            case.priority = calculate_priority(case.case_type, case.description)
            
            doctor = auto_assign_doctor(case)
            
            if doctor:
                case.assigned_doctor = doctor
                
                notification = Notification.objects.create(
                    user=doctor,
                    title="New Emergency Case 🚑",
                    message=f"You have been assigned to case #{case.id}"
                )

                channel_layer = get_channel_layer()
                room_name = f'notifications_{doctor.id}'
                notification_data = NotificationSerializer(notification).data
                
                async_to_sync(channel_layer.group_send)(
                    room_name,
                    {
                        'type': 'send.notification',
                        'message': notification_data
                    }
                )

            case.save()

            guide = EmergencyGuide.objects.filter(case_type=case.case_type).first()
            if guide:
                CaseResponse.objects.create(case=case, is_auto=True, message=guide.instructions)
            
            return Response({
                "message": "Case created successfully",
                "case_id": case.id,
                "priority": case.priority
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetCasesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=CaseListSerializer(many=True))
    def get(self, request):
        user = request.user
        if user.role == 'doctor':
            queryset = Case.objects.filter(Q(status='open', assigned_doctor=None) | Q(assigned_doctor=user))
        else:
            queryset = Case.objects.filter(created_by=user)
        cases = queryset.prefetch_related('responses').distinct().order_by('-created_at')
        serializer = CaseListSerializer(cases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class DoctorDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsDoctor]

    @extend_schema(responses=CaseListSerializer(many=True))
    def get(self, request):
        try:
            profile = request.user.doctorprofile
        except DoctorProfile.DoesNotExist:
            return Response({"error": "Doctor profile not found"}, status=404)
        matching_case_types = [ct for ct, sp in {'burn': 'burn', 'trauma': 'trauma', 'injury': 'surgery', 'general': 'general', 'fracture': 'trauma', 'other': 'general'}.items() if sp == profile.specialty]
        cases = Case.objects.filter((Q(status='open') & Q(case_type__in=matching_case_types)) | Q(assigned_doctor=request.user)).prefetch_related('responses').distinct().order_by('-priority', '-created_at')
        serializer = CaseListSerializer(cases, many=True)
        return Response(serializer.data)

class ClaimCaseView(APIView):
    permission_classes = [IsAuthenticated, IsDoctor]

    @extend_schema(request=None, responses={200: None})
    def post(self, request, case_id):
        case = get_object_or_404(Case, id=case_id, status='open', assigned_doctor=None)
        case.assigned_doctor = request.user
        case.status = 'in_progress'
        case.save()
        return Response({"message": "Case claimed successfully", "case_id": case.id})

class MyCasesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=CaseListSerializer(many=True))
    def get(self, request):
        user = request.user
        if user.role == 'doctor':
            queryset = Case.objects.filter(assigned_doctor=user)
        else:
            queryset = Case.objects.filter(created_by=user)
        cases = queryset.prefetch_related('responses').order_by('-created_at')
        serializer = CaseListSerializer(cases, many=True)
        return Response(serializer.data)



class PriorityCasesView(APIView):
    permission_classes = [IsAuthenticated, IsDoctor]

    @extend_schema(responses=CaseListSerializer(many=True))
    def get(self, request):
        high = Case.objects.filter(priority=3, status='open')
        medium = Case.objects.filter(priority=2, status='open')
        low = Case.objects.filter(priority=1, status='open')
        return Response({
            "high_priority": CaseListSerializer(high, many=True).data,
            "medium_priority": CaseListSerializer(medium, many=True).data,
            "low_priority": CaseListSerializer(low, many=True).data,
        })





class CaseImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, case_id):
        """
        واجهة لرفع صورة وربطها بحالة موجودة.
        """
        case = get_object_or_404(Case, id=case_id, created_by=request.user)
        
        image = request.data.get('image')
        if not image:
            return Response({"error": "Image file is required."}, status=status.HTTP_400_BAD_REQUEST)

        case_image = CaseImage.objects.create(case=case, image=image)
        
        compress_case_image(case_image.id)
        
        return Response({
            "message": "Image uploaded successfully. Compression is in progress.",
            "case_image_id": case_image.id
        }, status=status.HTTP_201_CREATED)
