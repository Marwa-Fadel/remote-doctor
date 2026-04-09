from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User, DoctorProfile
from cases.models import Case
from .models import Response

class ResponseAPITestCase(APITestCase):

    def setUp(self):
        """إعداد البيئة قبل كل اختبار."""
        # 1. إنشاء المستخدمين
        self.civilian_user = User.objects.create_user(username='patient', password='p', role='civilian')
        self.doctor_user = User.objects.create_user(username='doctor', password='p', role='doctor')
        DoctorProfile.objects.create(user=self.doctor_user, specialty='general')

        # 2. إنشاء حالة ليتم الرد عليها
        self.case = Case.objects.create(created_by=self.civilian_user, description='Test case', case_type='other')

        # 3. إعداد الرابط
        self.respond_url = reverse('doctor-respond') # افترضنا أن اسم الرابط هو 'doctor-respond'

    def test_doctor_can_respond(self):
        """API Test: التأكد من أن الطبيب يمكنه إضافة رد بنجاح."""
        # تسجيل الدخول كطبيب
        self.client.force_authenticate(user=self.doctor_user)

        data = {
            "case": self.case.id,
            "message": "This is a response from the doctor."
        }

        response = self.client.post(self.respond_url, data, format='json')

        # نتوقع نجاح العملية وتغيير حالة الحالة
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Response.objects.count(), 1)
        
        # التأكد من أن حالة الـ Case قد تم تحديثها
        self.case.refresh_from_db()
        self.assertEqual(self.case.status, 'under_treatment')
        self.assertEqual(Response.objects.first().responder, self.doctor_user)

    def test_civilian_cannot_respond(self):
        """API Test: التأكد من أن المريض لا يمكنه إضافة رد (خطأ صلاحيات)."""
        # تسجيل الدخول كمريض
        self.client.force_authenticate(user=self.civilian_user)

        data = {
            "case": self.case.id,
            "message": "A civilian trying to respond."
        }

        response = self.client.post(self.respond_url, data, format='json')

        # نتوقع أن يتم رفض الطلب (Forbidden)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Response.objects.count(), 0) # نتأكد من عدم إنشاء أي رد

    def test_unauthenticated_user_cannot_respond(self):
        """API Test: التأكد من أن المستخدم غير المسجل لا يمكنه إضافة رد."""
        # لا نقوم بتسجيل الدخول
        data = {
            "case": self.case.id,
            "message": "An unauthenticated user trying to respond."
        }

        response = self.client.post(self.respond_url, data, format='json')

        # نتوقع أن يتم رفض الطلب (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Response.objects.count(), 0)
