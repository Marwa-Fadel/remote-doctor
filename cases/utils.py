from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from users.models import DoctorProfile, User # استيراد User مباشرة
from .models import Case

def match_doctor_specialty(case_type):
    """
    Returns the required specialty for a given case type.
    """
    mapping = {
        'burn': 'burn',
        'trauma': 'trauma',
        'injury': 'surgery',
        'general': 'general',
        'fracture': 'trauma', # إضافة للتعامل مع الكسور
        'other': 'general',
    }
    return mapping.get(case_type, 'general')


def calculate_priority(case_type, description):
    """
    Calculates the priority of a case based on its type and description.
    Returns an integer (1=Low, 2=Medium, 3=High).
    """
    if case_type in ['burn', 'trauma']:
        return 3  # High
    if case_type == 'injury' and "bleeding" in description.lower():
        return 3  # High
    if case_type == 'injury':
        return 2  # Medium
    return 1  # Low


def auto_assign_doctor(case: Case):
    """
    Finds the best available doctor for a case with maximum efficiency.
    This function now uses a single database query to avoid the N+1 problem.
    """
    required_specialty = match_doctor_specialty(case.case_type)

    
    best_doctor = User.objects.filter(
        role='doctor',
        is_available=True,
        doctorprofile__specialty=required_specialty
    ).annotate(
        open_cases_count=Count('assigned_cases', filter=Q(assigned_cases__status='open'))
    ).order_by('open_cases_count').first()

    return best_doctor
