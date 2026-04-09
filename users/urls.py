from django.urls import path
from .views import (
    RegisterView, 
    CustomTokenObtainPairView, 
    UserProfileView, 
    DoctorListView,
    EmergencyLoginView 
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # --- بوابة الطوارئ ---
    # POST /api/users/emergency-login/
    path('emergency-login/', EmergencyLoginView.as_view(), name='emergency-login'),

    # --- بوابة الحسابات التقليدية ---
    # POST /api/users/register/
    path('register/', RegisterView.as_view(), name='user-register'),
    
    # POST /api/users/login/
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # POST /api/users/login/refresh/
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # GET, PUT, PATCH /api/users/me/
    path('me/', UserProfileView.as_view(), name='user-profile'),
    
    # GET /api/users/doctors/
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
]
