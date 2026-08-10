from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from .models import Subscription

User = get_user_model()


@shared_task
def send_course_update_email(course_id, course_name, user_email):
    """Отправка письма об обновлении курса"""
    subject = f'Курс "{course_name}" был обновлен!'
    message = f"""
    Здравствуйте!

    Курс "{course_name}" был обновлен. 
    Новые материалы уже доступны для изучения.

    Ссылка на курс: http://localhost:8000/api/v1/courses/{course_id}/

    С уважением,
     Админ
    """
    send_mail(
        subject,
        message,
        'noreply@lms.com',
        [user_email],
        fail_silently=False,
    )


@shared_task
def block_inactive_users():
    """Блокировка пользователей, которые не заходили более месяца"""
    month_ago = timezone.now() - timedelta(days=30)

    inactive_users = User.objects.filter(
        last_login__lt=month_ago,
        is_active=True,
        is_superuser=False,
    )

    count = inactive_users.count()
    inactive_users.update(is_active=False)

    return f'Блокировано {count} неактивных пользователей'


@shared_task
def debug_task():
    """Тестовая задача"""
    print("Celery работает!")
    return "Celery работает!"


@shared_task
def send_course_update_notifications(course_id, course_name):
    """Отправка уведомлений всем подписчикам курса"""
    from .models import Subscription

    subscriptions = Subscription.objects.filter(course_id=course_id)
    emails = subscriptions.values_list('user__email', flat=True)

    if not emails:
        return f'Нет подписчиков для курса "{course_name}"'

    subject = f'Обновление курса "{course_name}"'
    message = f"""
    Здравствуйте!

    Курс "{course_name}" был обновлен. 
    Новые материалы уже доступны для изучения.

    Ссылка на курс: http://localhost:8000/api/v1/courses/{course_id}/

    С уважением,
    Админ
    """

    for email in emails:
        send_mail(
            subject,
            message,
            'noreply@lms.com',
            [email],
            fail_silently=False,
        )

    return f'Отправлено {len(emails)} уведомлений для курса "{course_name}"'
