from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User
from .models import EmergencyGuide

class EmergencyGuideAPITestCase(APITestCase):

    def setUp(self):
        """إعداد البيئة قبل كل اختبار."""
        self.user = User.objects.create_user(username='testuser', password='p')

        EmergencyGuide.objects.create(case_type='burn', title='Burn First Aid', instructions='Cool the burn...')
        EmergencyGuide.objects.create(case_type='bleeding', title='Bleeding First Aid', instructions='Apply pressure...')

        self.list_guides_url = reverse('list-guides')



    def test_list_guides_for_authenticated_user(self):
        """API Test: التأكد من أن المستخدم المسجل يمكنه عرض قائمة الإرشادات."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.list_guides_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'Burn First Aid')

    def test_list_guides_for_unauthenticated_user(self):
        """API Test: التأكد من منع المستخدم غير المسجل من عرض القائمة."""
        
        response = self.client.get(self.list_guides_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
