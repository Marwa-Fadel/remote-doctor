from django.urls import path
from .views import CreateCaseView, GetCasesView, DoctorDashboardView, ClaimCaseView, MyCasesView, PriorityCasesView,CaseImageView

urlpatterns = [
    path('create/', CreateCaseView.as_view(), name='case-create'),
    path('list/', GetCasesView.as_view(), name='case-list'),
    path('dashboard/', DoctorDashboardView.as_view(), name='doctor-dashboard'),
    path('claim/<int:case_id>/', ClaimCaseView.as_view(), name='case-claim'),
    path('my-cases/', MyCasesView.as_view(), name='my-cases'),
    path('priority/', PriorityCasesView.as_view(), name='priority-cases'),
    path('<int:case_id>/upload-image/', CaseImageView.as_view(), name='case-upload-image'),

]
