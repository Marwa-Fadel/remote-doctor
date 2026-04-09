from rest_framework.views import APIView
from rest_framework.response import Response as DRFResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .permissions import IsDoctor
from .serializers import DoctorResponseSerializer
from drf_spectacular.utils import extend_schema

class DoctorRespondView(APIView):
    permission_classes = [IsAuthenticated, IsDoctor]
    
    # 💡 قمنا بإضافة هذا المزخرف
    @extend_schema(
        request=DoctorResponseSerializer,
        responses={201: {"description": "Response added successfully"}}
    )
    def post(self, request):
        serializer = DoctorResponseSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            case_instance = serializer.validated_data['case']
            response_obj = serializer.save(
                responder=request.user,
                is_auto=False
            )
            case_instance.status = 'under_treatment'
            case_instance.save()
            return DRFResponse({
                "message": "Response added successfully",
                "response_id": response_obj.id
            }, status=status.HTTP_201_CREATED)
        return DRFResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
