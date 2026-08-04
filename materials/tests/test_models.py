from django.test import TestCase
from django.contrib.auth import get_user_model
from materials.models import Course, Lesson

User = get_user_model()


class CourseModelTest(TestCase):
    """Тесты для модели Course"""

    def setUp(self):
        """Тестовые данные"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='test123456',
            first_name='Test'
        )
        self.course = Course.objects.create(
            name='Тестовый курс',
            description='Описание тестового курса',
            owner=self.user
        )

    def test_course_creation(self):
        """Проверяем создание курса"""
        self.assertEqual(self.course.name, 'Тестовый курс')
        self.assertEqual(self.course.owner, self.user)
        self.assertTrue(self.course.created_at)

    def test_course_str(self):
        """Проверяем строковое представление"""
        self.assertEqual(str(self.course), 'Тестовый курс')


class LessonModelTest(TestCase):
    """Тесты для модели Lesson"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='test123456'
        )
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

    def test_lesson_creation(self):
        """Проверяем создание урока"""
        self.assertEqual(self.lesson.name, 'Тестовый урок')
        self.assertEqual(self.lesson.course, self.course)
        self.assertEqual(self.lesson.owner, self.user)

    def test_lesson_str(self):
        """Проверяем строковое представление"""
        expected = 'Тестовый урок (курс: Тестовый курс)'
        self.assertEqual(str(self.lesson), expected)