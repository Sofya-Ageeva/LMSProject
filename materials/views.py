from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Course, Lesson
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import CourseSerializer, LessonSerializer, LessonDetailSerializer
from .paginators import CoursePagination, LessonPagination
from users.permissions import IsModerator, IsOwner, IsOwnerOrModerator, IsOwnerOrReadOnly, IsOwnerOrAdmin

class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для управления курсами."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CoursePagination

    def get_permissions(self):
        """Разные права для разных действий"""
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        elif self.action == 'update' or self.action == 'partial_update':
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action == 'list' or self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """При создании курса привязываем владельца"""
        user = self.request.user

        if user.groups.filter(name='moderators').exists():
            raise PermissionDenied("Модераторы не могут создавать курсы")

        serializer.save(owner=user)

    def get_queryset(self):
        """Фильтруем курсы в зависимости от прав"""
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return Course.objects.all()

        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()

        return Course.objects.filter(owner=user)

    def create(self, request, *args, **kwargs):
        """Создание нового курса."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Обновление курса."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        self.check_object_permissions(request, instance)
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
        self.check_object_permissions(request, instance)
        self.perform_destroy(instance)
        return Response(
            {'message': 'Курс успешно удален'},
            status=status.HTTP_204_NO_CONTENT
        )


class LessonListCreateView(ListCreateAPIView):
    """
    Generic-класс для:
    - GET /lessons/ - получение списка уроков
    - POST /lessons/ - создание нового урока
    """

    queryset = Lesson.objects.select_related('course').all()
    permission_classes = [IsAuthenticated]
    pagination_class = LessonPagination

    def get_permissions(self):
        """Разные права для разных методов"""
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от метода запроса"""
        if self.request.method == 'GET':
            return LessonDetailSerializer
        return LessonSerializer

    def perform_create(self, serializer):
        """Создание урока с проверкой наличия курса"""
        course_id = self.request.data.get('course')
        user = self.request.user

        if not course_id:
            raise ValidationError({'course': 'Поле course обязательно'})

        try:
            course = Course.objects.get(id=course_id)
            if not user.groups.filter(name='moderators').exists():
                if course.owner and course.owner != user:
                    raise PermissionDenied('У вас нет доступа для создания урока в этом курсе')
            serializer.save(course=course)
        except Course.DoesNotExist:
            raise ValidationError({'course': 'Курс с таким ID не найден'})

    def get_queryset(self):
        """Фильтруем уроки в зависимости от прав"""
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Lesson.objects.all()

        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)

class LessonRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """Generic-класс для работы с одним уроком"""

    queryset = Lesson.objects.select_related('course', 'owner').all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Разные права для разных методов"""
        if self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        elif self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от метода запроса"""
        if self.request.method == 'GET':
            return LessonDetailSerializer
        return LessonSerializer

    def update(self, request, *args, **kwargs):
        """Обновление урока с проверкой курса"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        self.check_object_permissions(request, instance)

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

    def get_queryset(self):
        """Фильтруем уроки в зависимости от прав"""
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return Lesson.objects.all()

        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)
