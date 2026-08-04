from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from materials.models import Course, Lesson

User = get_user_model()


class LessonAPITestCase(TestCase):
    """Тесты для API уроков"""

    def setUp(self):
        """Тестовые данные"""
        self.user = User.objects.create_user(
            email='user@example.com',
            password='test123456',
            first_name='User'
        )

        self.moderator = User.objects.create_user(
            email='moderator@example.com',
            password='test123456',
            first_name='Moderator'
        )

        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='test123456'
        )

        group, _ = Group.objects.get_or_create(name='moderators')
        self.moderator.groups.add(group)
        self.moderator.save()

        self.course = Course.objects.create(
            name='Тестовый курс',
            owner=self.user
        )

        self.lesson = Lesson.objects.create(
            course=self.course,
            name='Тестовый урок',
            description='Описание урока',
            video_link='https://www.youtube.com/watch?v=test',
            owner=self.user
        )

        self.client = APIClient()

    def test_create_lesson_as_user(self):
        """Тест создания урока пользователем"""
        self.client.force_authenticate(user=self.user)

        data = {
            'course': self.course.id,
            'name': 'Новый урок',
            'description': 'Описание нового урока',
            'video_link': 'https://www.youtube.com/watch?v=new'
        }

        response = self.client.post('/api/v1/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_lesson_with_invalid_url(self):
        """Тест создания урока с невалидной ссылкой"""
        self.client.force_authenticate(user=self.user)

        data = {
            'course': self.course.id,
            'name': 'Урок с VK',
            'video_link': 'https://vk.com/video/abc'
        }

        response = self.client.post('/api/v1/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_link', response.data)

    def test_create_lesson_as_moderator(self):
        """Тест: модератор НЕ может создавать уроки"""
        self.client.force_authenticate(user=self.moderator)

        data = {
            'course': self.course.id,
            'name': 'Урок от модератора',
            'video_link': 'https://www.youtube.com/watch?v=test'
        }

        response = self.client.post('/api/v1/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_own_lesson(self):
        """Тест обновления своего урока"""
        self.client.force_authenticate(user=self.user)

        data = {'name': 'Обновленный урок'}
        response = self.client.patch(
            f'/api/v1/lessons/{self.lesson.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, 'Обновленный урок')

    def test_delete_own_lesson(self):
        """Тест удаления своего урока"""
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(f'/api/v1/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_other_lesson(self):
        """Тест удаления чужого урока"""
        self.client.force_authenticate(user=self.moderator)

        response = self.client.delete(f'/api/v1/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
