from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from materials.models import Course, Lesson
from materials.serializers import LessonSerializer
from materials.validators import validate_youtube_url

User = get_user_model()


class LessonSerializerTest(TestCase):
    """Тесты для LessonSerializer"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='test123456'
        )
        self.course = Course.objects.create(
            name='Тестовый курс',
            owner=self.user
        )

    def test_valid_youtube_url(self):
        """Проверка валидной ссылки"""
        data = {
            'course': self.course.id,
            'name': 'Урок с YouTube',
            'video_link': 'https://www.youtube.com/watch?v=abc123'
        }
        serializer = LessonSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_youtube_url(self):
        """Проверка невалидной ссылки"""
        data = {
            'course': self.course.id,
            'name': 'Урок с VK',
            'video_link': 'https://vk.com/video/abc123'
        }
        serializer = LessonSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('video_link', serializer.errors)

    def test_validate_youtube_url_function(self):
        """Тестируем функцию-валидатор"""
        valid_url = 'https://www.youtube.com/watch?v=abc123'
        self.assertEqual(validate_youtube_url(valid_url), valid_url)

        invalid_url = 'https://vk.com/video/abc123'
        with self.assertRaises(ValidationError):
            validate_youtube_url(invalid_url)
