from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User, DoctorProfile

class UserAuthAPITestCase(APITestCase):

    def setUp(self):
        """إعداد الروابط التي سنستخدمها في الاختبارات."""
        self.register_url = reverse('user-register')
        self.login_url = reverse('token_obtain_pair')
        self.profile_url = reverse('user-profile')

    def test_register_civilian_successfully(self):
        """API Test: التأكد من نجاح تسجيل مريض جديد ببيانات صحيحة."""
        data = {
            "username": "newcivilian",
            "password": "password123",
            "role": "civilian",
            "first_name": "John",
            "phone_number": "1234567890"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'newcivilian')

    def test_register_doctor_successfully(self):
        """API Test: التأكد من نجاح تسجيل طبيب جديد مع التخصص."""
        data = {
            "username": "newdoctor",
            "password": "password123",
            "role": "doctor",
            "first_name": "Dr. Jane",
            "specialty": "burn"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(DoctorProfile.objects.count(), 1)
        self.assertEqual(DoctorProfile.objects.get().specialty, 'burn')

    def test_register_doctor_missing_specialty_fails(self):
        """API Test: التأكد من فشل تسجيل طبيب بدون تحديد التخصص."""
        data = {
            "username": "anotherdoctor",
            "password": "password123",
            "role": "doctor"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('specialty', response.data)

    def test_login_and_profile_view(self):
        """API Test: اختبار عملية تسجيل الدخول ثم عرض الملف الشخصي."""
        user = User.objects.create_user(username='testuser', password='testpassword', first_name='Test')
        
        wrong_data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(self.login_url, wrong_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        correct_data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(self.login_url, correct_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)
        
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['first_name'], 'Test')



    def test_emergency_login_flow(self):
        """API Test: اختبار كامل لسيناريو بوابة الطوارئ."""
        emergency_login_url = reverse('emergency-login')
        
        data = {"phone_number": "0998765432"}
        response = self.client.post(emergency_login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertTrue(User.objects.filter(username="0998765432").exists())
        new_user = User.objects.get(username="0998765432")
        self.assertEqual(new_user.role, 'civilian')

        response = self.client.post(emergency_login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(User.objects.count(), 1)
