from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django.db.models import Q
from django.utils.crypto import get_random_string 

from .models import User
from .serializers import RegisterSerializer, UserSerializer, DoctorDetailSerializer, EmergencyLoginSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(username=request.data['username'])
            serializer = UserSerializer(user)
            response.data['user'] = serializer.data
        return response


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class DoctorListView(generics.ListAPIView):
    queryset = User.objects.filter(role='doctor', is_available=True)
    serializer_class = DoctorDetailSerializer
    permission_classes = [IsAuthenticated]


class EmergencyLoginView(generics.GenericAPIView):
    serializer_class = EmergencyLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']

        user = User.objects.filter(Q(phone_number=phone_number) | Q(username=phone_number)).first()

        if not user:
            if User.objects.filter(username=phone_number).exists():
                return Response(
                    {"error": "A user with this username already exists. Please contact support."},
                    status=status.HTTP_409_CONFLICT
                )
            
            password = get_random_string(12)
            
            user = User.objects.create_user(
                username=phone_number,
                password=password,
                phone_number=phone_number,
                role='civilian'
            )

        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data
        }, status=status.HTTP_200_OK)
