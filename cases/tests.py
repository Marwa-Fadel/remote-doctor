from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User, DoctorProfile
from .models import Case
from .utils import calculate_priority, auto_assign_doctor

#  UNIT TESTS (اختبارات الوحدة للوظائف المنطقية)

class UtilsTestCase(TestCase):
    
    def test_calculate_priority_logic(self):
        """Unit Test: اختبار منطق دالة حساب الأولوية."""
        self.assertEqual(calculate_priority('burn', '...'), 3, "Burn case should be high priority")
        self.assertEqual(calculate_priority('trauma', '...'), 3, "Trauma case should be high priority")
        self.assertEqual(calculate_priority('injury', '...bleeding...'), 3, "Bleeding injury should be high priority")
        self.assertEqual(calculate_priority('injury', '...'), 2, "Normal injury should be medium priority")
        self.assertEqual(calculate_priority('other', '...'), 1, "Other cases should be low priority")

    def test_auto_assign_doctor(self):
        """Unit Test: اختبار دقيق لدالة التعيين التلقائي للطبيب."""
        surgeon1 = User.objects.create_user(username='surgeon1', password='p', role='doctor')
        DoctorProfile.objects.create(user=surgeon1, specialty='surgery')
        
        surgeon2 = User.objects.create_user(username='surgeon2', password='p', role='doctor')
        DoctorProfile.objects.create(user=surgeon2, specialty='surgery')

        burn_doctor = User.objects.create_user(username='burn_doc', password='p', role='doctor')
        DoctorProfile.objects.create(user=burn_doctor, specialty='burn')
        
        patient = User.objects.create_user(username='patient', password='p', role='civilian')

        Case.objects.create(created_by=patient, description='...', case_type='injury', assigned_doctor=surgeon1, status='open')

        new_injury_case = Case.objects.create(created_by=patient, description='...', case_type='injury')
        assigned_doctor = auto_assign_doctor(new_injury_case)
        self.assertEqual(assigned_doctor, surgeon2, "Should assign to the surgeon with fewer cases")

        burn_case = Case.objects.create(created_by=patient, description='...', case_type='burn')
        assigned_doctor = auto_assign_doctor(burn_case)
        self.assertEqual(assigned_doctor, burn_doctor, "Should assign to the burn specialist")
        
        surgeon2.is_available = False
        surgeon2.save()
        another_injury_case = Case.objects.create(created_by=patient, description='...', case_type='injury')
        assigned_doctor = auto_assign_doctor(another_injury_case)
        self.assertEqual(assigned_doctor, surgeon1, "Should assign to the only available surgeon")


#  API / INTEGRATION TESTS (اختبارات التكامل للواجهات البرمجية)


class CaseAPITestCase(APITestCase):

    def setUp(self):
        """إعداد البيئة قبل كل اختبار API."""
        self.civilian_user = User.objects.create_user(username='testcivilian', password='p', role='civilian')
        self.doctor_user1 = User.objects.create_user(username='testdoctor1', password='p', role='doctor', is_available=True)
        DoctorProfile.objects.create(user=self.doctor_user1, specialty='surgery')
        self.doctor_user2 = User.objects.create_user(username='testdoctor2', password='p', role='doctor', is_available=True)
        DoctorProfile.objects.create(user=self.doctor_user2, specialty='burn')

        self.create_case_url = reverse('case-create')
        self.dashboard_url = reverse('doctor-dashboard')

    def test_create_case_unauthenticated(self):
        """API Test: رفض إنشاء حالة لمستخدم غير مسجل دخوله."""
        response = self.client.post(self.create_case_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_case_as_civilian(self):
        """API Test: نجاح إنشاء حالة من قبل مريض مسجل دخوله."""
        self.client.force_authenticate(user=self.civilian_user)
        case_data = {"description": "Patient has a severe burn", "case_type": "burn"}
        response = self.client.post(self.create_case_url, case_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_case = Case.objects.first()
        self.assertEqual(created_case.assigned_doctor, self.doctor_user2)

    def test_claim_case_logic(self):
        """API Test: اختبار دقيق لعملية استلام الحالة."""
        case = Case.objects.create(created_by=self.civilian_user, description='...', case_type='surgery', status='open')
        claim_url = reverse('case-claim', kwargs={'case_id': case.id})

        self.client.force_authenticate(user=self.civilian_user)
        response = self.client.post(claim_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.doctor_user2)
        response = self.client.post(claim_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        case.refresh_from_db()
        self.assertEqual(case.assigned_doctor, self.doctor_user2)
        self.assertEqual(case.status, 'in_progress')

        self.client.force_authenticate(user=self.doctor_user1)
        response = self.client.post(claim_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 

    def test_doctor_dashboard_content(self):
        """API Test: التأكد من أن لوحة تحكم الطبيب تعرض المحتوى الصحيح."""
        Case.objects.create(created_by=self.civilian_user, description='burn case', case_type='burn', status='open')
        Case.objects.create(created_by=self.civilian_user, description='surgery case', case_type='injury', status='open')
        Case.objects.create(created_by=self.civilian_user, description='closed case', case_type='burn', status='closed')
        
        self.client.force_authenticate(user=self.doctor_user2)
        response = self.client.get(self.dashboard_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['description'], 'burn case')
