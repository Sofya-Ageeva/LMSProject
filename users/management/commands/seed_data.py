from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from materials.models import Course, Lesson
from users.models import Payment

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем заполнение базы данных...')

        # Создаем пользователей
        admin, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'first_name': 'Admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Создан админ: {admin.email}'))

        user, created = User.objects.get_or_create(
            email='user@example.com',
            defaults={
                'first_name': 'Иван',
                'last_name': 'Петров',
                'phone': '+7-999-987-65-43',
                'city': 'Санкт-Петербург'
            }
        )
        if created:
            user.set_password('user123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Создан пользователь: {user.email}'))

        # Создаем курсы
        course1, created = Course.objects.get_or_create(
            name='Python для начинающих',
            defaults={
                'description': 'Полный курс по Python с нуля'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан курс: {course1.name}'))

        course2, created = Course.objects.get_or_create(
            name='Django для профессионалов',
            defaults={
                'description': 'Углубленный курс по Django'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан курс: {course2.name}'))

        # Создаем уроки
        lesson1, created = Lesson.objects.get_or_create(
            course=course1,
            name='Введение в Python',
            defaults={
                'description': 'Установка и первая программа',
                'video_link': 'https://www.youtube.com/watch?v=example1'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан урок: {lesson1.name}'))

        lesson2, created = Lesson.objects.get_or_create(
            course=course1,
            name='Переменные и типы данных',
            defaults={
                'description': 'Основы работы с данными',
                'video_link': 'https://www.youtube.com/watch?v=example2'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан урок: {lesson2.name}'))

        lesson3, created = Lesson.objects.get_or_create(
            course=course2,
            name='Введение в Django',
            defaults={
                'description': 'Структура Django проекта',
                'video_link': 'https://www.youtube.com/watch?v=example3'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан урок: {lesson3.name}'))

        # Создаем платежи
        payment1, created = Payment.objects.get_or_create(
            user=admin,
            paid_course=course1,
            paid_lesson=None,
            defaults={
                'amount': '5000.00',
                'payment_method': 'cash'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан платеж: {payment1.amount} руб.'))

        payment2, created = Payment.objects.get_or_create(
            user=admin,
            paid_course=None,
            paid_lesson=lesson1,
            defaults={
                'amount': '1500.00',
                'payment_method': 'transfer'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан платеж: {payment2.amount} руб.'))

        payment3, created = Payment.objects.get_or_create(
            user=user,
            paid_course=course2,
            paid_lesson=None,
            defaults={
                'amount': '3000.00',
                'payment_method': 'cash'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан платеж: {payment3.amount} руб.'))

        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена!'))

        self.stdout.write('Статистика:')
        self.stdout.write(f'Пользователей: {User.objects.count()}')
        self.stdout.write(f'Курсов: {Course.objects.count()}')
        self.stdout.write(f'Уроков: {Lesson.objects.count()}')
        self.stdout.write(f'Платежей: {Payment.objects.count()}')
