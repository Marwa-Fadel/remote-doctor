from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User
from .models import Notification

class NotificationAPITestCase(APITestCase):

    def setUp(self):
        """إعداد البيئة قبل كل اختبار."""
        self.user1 = User.objects.create_user(username='user1', password='p')
        self.user2 = User.objects.create_user(username='user2', password='p')

        self.notification1_user1 = Notification.objects.create(user=self.user1, title='Welcome user1', message='...')
        self.notification2_user1 = Notification.objects.create(user=self.user1, title='Update for user1', message='...')
        self.notification1_user2 = Notification.objects.create(user=self.user2, title='Hello user2', message='...')
        self.list_url = reverse('notification-list')


    def test_list_notifications_for_user1(self):
        """API Test: التأكد من أن المستخدم الأول يرى إشعاراته فقط."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        response_titles = [item['title'] for item in response.data]
        
        self.assertIn('Welcome user1', response_titles)
        self.assertIn('Update for user1', response_titles)



    def test_list_notifications_for_user2(self):
        """API Test: التأكد من أن المستخدم الثاني يرى إشعاره فقط."""
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Hello user2')



    def test_mark_own_notification_as_read(self):
        """API Test: التأكد من أن المستخدم يمكنه تحديد إشعاره كمقروء."""
        self.client.force_authenticate(user=self.user1)
        
        self.assertFalse(self.notification1_user1.is_read)
        
        mark_read_url = reverse('notification-mark-read', kwargs={'pk': self.notification1_user1.id})
        
        response = self.client.post(mark_read_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.notification1_user1.refresh_from_db()
        self.assertTrue(self.notification1_user1.is_read)



    def test_cannot_mark_others_notification_as_read(self):
        """API Test: التأكد من أن المستخدم لا يمكنه تعديل إشعارات غيره."""
        self.client.force_authenticate(user=self.user1)
        
        mark_read_url = reverse('notification-mark-read', kwargs={'pk': self.notification1_user2.id})
        
        response = self.client.post(mark_read_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.notification1_user2.refresh_from_db()
        self.assertFalse(self.notification1_user2.is_read)
