from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    """Менеджер пользователей"""

    def create_user(self, email, password=None, **extra_fields):
        """Создание обычного пользователя"""
        if not email:
            raise ValueError('Email обязателен для заполнения')

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создание суперпользователя (администратора)"""

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Пользовательская модель с авторизацией по email вместо username"""
    email = models.EmailField(
        unique=True,
        verbose_name='Email адрес'
    )

    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя'
    )

    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия'
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон'
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Город'
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватарка'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name='Персонал (доступ к админке)'
    )

    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата регистрации'
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        """Отображение объекта в админке"""
        return self.email

    def get_full_name(self):
        """Полное имя пользователя"""
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email

    def get_short_name(self):
        """Краткое имя"""
        return self.first_name or self.email


class Payment(models.Model):
    """Модель платежа пользователя за курс или урок"""

    # Способ оплаты
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Наличные'
        TRANSFER = 'transfer', 'Перевод на счет'

    # Связь с пользователем
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Пользователь'
    )

    # Дата оплаты
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата оплаты'
    )

    # Оплаченный курс
    paid_course = models.ForeignKey(
        'materials.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='Оплаченный курс'
    )

    # Оплаченный урок
    paid_lesson = models.ForeignKey(
        'materials.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='Оплаченный урок'
    )

    # Сумма оплаты
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма оплаты'
    )

    # Способ оплаты
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        verbose_name='Способ оплаты'
    )

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Платеж {self.user.email} - {self.amount} руб."

    def clean(self):
        """Проверка оплаты"""
        if not self.paid_course and not self.paid_lesson:
            raise ValidationError('Должен быть оплачен либо курс, либо урок')
        if self.paid_course and self.paid_lesson:
            raise ValidationError('Нельзя оплатить одновременно и курс, и урок')


class Subscription(models.Model):
    """Модель подписки пользователя на обновления курса"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )

    course = models.ForeignKey(
        'materials.Course',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Курс'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'course')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} → {self.course.name}"
