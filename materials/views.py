from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer, LessonDetailSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления курсами.
    Предоставляет все CRUD операции:
    - GET /courses/ - список курсов
    - POST /courses/ - создание курса
    - GET /courses/{id}/ - детали курса
    - PUT /courses/{id}/ - полное обновление
    - PATCH /courses/{id}/ - частичное обновление
    - DELETE /courses/{id}/ - удаление курса
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def create(self, request, *args, **kwargs):
        """Создание нового курса."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Обновление курса."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Удаление курса."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Курс успешно удален'},
            status=status.HTTP_204_NO_CONTENT
        )


from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.exceptions import ValidationError


class LessonListCreateView(ListCreateAPIView):
    """
    Generic-класс для:
    - GET /lessons/ - получение списка уроков
    - POST /lessons/ - создание нового урока
    """

    queryset = Lesson.objects.select_related('course').all()

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от метода запроса"""
        if self.request.method == 'GET':
            return LessonDetailSerializer
        return LessonSerializer

    def perform_create(self, serializer):
        """Создание урока с проверкой наличия курса"""
        course_id = self.request.data.get('course')

        if not course_id:
            raise ValidationError({'course': 'Поле course обязательно'})

        try:
            course = Course.objects.get(id=course_id)
            serializer.save(course=course)
        except Course.DoesNotExist:
            raise ValidationError({'course': 'Курс с таким ID не найден'})


class LessonRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """Generic-класс для работы с одним уроком"""

    queryset = Lesson.objects.select_related('course').all()

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от метода запроса"""
        if self.request.method == 'GET':
            return LessonDetailSerializer
        return LessonSerializer

    def update(self, request, *args, **kwargs):
        """Обновление урока с проверкой курса"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)

        course_id = request.data.get('course')
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                serializer.validated_data['course'] = course
            except Course.DoesNotExist:
                raise ValidationError({'course': 'Курс с таким ID не найден'})

        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        """Сохранение обновленного урока"""
        serializer.save()

    def perform_destroy(self, instance):
        """Удаление урока"""
        instance.delete()

