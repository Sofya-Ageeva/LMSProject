from django.contrib import admin
from .models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Настройка отображения курсов в админке"""

    list_display = ['id', 'name', 'created_at', 'updated_at']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Настройка отображения уроков в админке"""

    list_display = ['id', 'name', 'course', 'created_at']
    list_display_links = ['id', 'name']
    list_filter = ['course', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['course', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
