from rest_framework import serializers
from .models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Course"""

    lesson_count = serializers.IntegerField(
        source='lessons.count',
        read_only=True
    )

    lessons = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Course
        fields = [
            'id',
            'name',
            'preview',
            'description',
            'created_at',
            'updated_at',
            'lesson_count',
            'lessons'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LessonSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для модели Lesson"""

    class Meta:
        model = Lesson
        fields = [
            'id',
            'course',
            'name',
            'description',
            'preview',
            'video_link',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LessonDetailSerializer(LessonSerializer):
    """Добавляет название курса"""

    course_name = serializers.CharField(
        source='course.name',
        read_only=True
    )

    class Meta(LessonSerializer.Meta):
        fields = LessonSerializer.Meta.fields + ['course_name']