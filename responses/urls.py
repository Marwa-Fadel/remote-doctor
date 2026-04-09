from django.urls import path
from .views import DoctorRespondView

urlpatterns = [
    # 💡 إضافة name='doctor-respond'
    path('respond/', DoctorRespondView.as_view(), name='doctor-respond'),
]
