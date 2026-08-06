from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from materials.models import Course
from users.models import Subscription

User = get_user_model()


class SubscriptionAPITestCase(TestCase):
    """Тесты для подписки на курс"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='test123456'
        )
        self.course = Course.objects.create(
            name='Тестовый курс',
            owner=self.user
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_subscribe_to_course(self):
        """Тест подписки на курс"""

        response = self.client.post('/api/v1/subscriptions/', {
            'course_id': self.course.id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(response.data['is_subscribed'])
        self.assertEqual(Subscription.objects.count(), 1)

    def test_unsubscribe_from_course(self):
        """Тест отписки от курса"""
        Subscription.objects.create(user=self.user, course=self.course)
        response = self.client.post('/api/v1/subscriptions/', {
            'course_id': self.course.id},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(response.data['is_subscribed'])
        self.assertEqual(Subscription.objects.count(), 0)

    def test_subscribe_without_course_id(self):
        """Тест подписки без указания курса"""

        response = self.client.post('/api/v1/subscriptions/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_subscribe_to_nonexistent_course(self):
        """Тест подписки на несуществующий курс"""

        response = self.client.post('/api/v1/subscriptions/', {
            'course_id': 999},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_check_subscription_status(self):
        """Тест проверки статуса подписки"""

        Subscription.objects.create(user=self.user, course=self.course)

        response = self.client.get('/api/v1/subscriptions/?course_id=1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])

    def test_is_subscribed_field_in_course(self):
        """Тест поля is_subscribed в сериализаторе курса"""
        Subscription.objects.create(user=self.user, course=self.course)

        response = self.client.get(f'/api/v1/courses/{self.course.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])
