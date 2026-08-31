from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_url

class LessonSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для модели Lesson"""

    video_link = serializers.URLField(
        validators=[validate_youtube_url],
        required=False,
        allow_blank=True
    )
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    class Meta:
        model = Lesson
        fields = [
            'id',
            'course',
            'name',
            'description',
            'preview',
            'video_link',
            'owner',
            'owner_email',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Course"""

    lesson_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = [
            'id',
            'name',
            'preview',
            'description',
            'owner',
            'owner_email',
            'created_at',
            'updated_at',
            'lesson_count',
            'lessons',
            'is_subscribed'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_lesson_count(self, obj):
        """Возвращает общее количество уроков в курсе"""
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.subscriptions.filter(user=request.user).exists()


class LessonDetailSerializer(LessonSerializer):
    """Добавляет название курса"""

    course_name = serializers.CharField(
        source='course.name',
        read_only=True
    )

    class Meta(LessonSerializer.Meta):
        fields = LessonSerializer.Meta.fields + ['course_name']