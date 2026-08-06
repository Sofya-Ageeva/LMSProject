from django.db import models
from django.conf import settings


class Course(models.Model):
    """Модель курса."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название курса'
    )
    preview = models.ImageField(
        upload_to='course_previews/',
        blank=True,
        null=True,
        verbose_name='Превью (изображение)'
    )

    description = models.TextField(
        blank=True,
        verbose_name='Описание курса'
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='Владелец курса',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Lesson(models.Model):
    """Модель урока."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Курс'
    )

    name = models.CharField(
        max_length=200,
        verbose_name='Название урока'
    )

    description = models.TextField(
        blank=True,
        verbose_name='Описание урока'
    )

    preview = models.ImageField(
        upload_to='lesson_previews/',
        blank=True,
        null=True,
        verbose_name='Превью (изображение)'
    )

    video_link = models.URLField(
        blank=True,
        verbose_name='Ссылка на видео'
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Владелец урока',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} (курс: {self.course.name})"
