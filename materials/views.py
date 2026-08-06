from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer, LessonDetailSerializer
from .paginators import CoursePagination, LessonPagination
from users.permissions import IsModerator, IsOwner, IsOwnerOrModerator, IsOwnerOrReadOnly, IsOwnerOrAdmin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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

    @swagger_auto_schema(
        operation_description="Получить список всех курсов с пагинацией",
        responses={
            200: CourseSerializer(many=True),
            401: "Неавторизован",
        }
    )
    def list(self, request, *args, **kwargs):
        """Получение списка курсов"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создать новый курс",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Название курса'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Описание курса'),
                'preview': openapi.Schema(type=openapi.TYPE_STRING, description='URL превью', nullable=True),
            }
        ),
        responses={
            201: openapi.Response('Курс создан', CourseSerializer),
            400: 'Ошибка валидации',
            401: 'Неавторизован',
            403: 'Доступ запрещен (модераторы не могут создавать курсы)',
        }
    )
    def create(self, request, *args, **kwargs):
        """Создание нового курса."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Получить детальную информацию о курсе",
        responses={
            200: CourseSerializer(),
            401: 'Неавторизован',
            404: 'Курс не найден',
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Получение деталей курса"""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Обновить курс (частичное или полное)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Название курса'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Описание курса'),
                'preview': openapi.Schema(type=openapi.TYPE_STRING, description='URL превью', nullable=True),
            }
        ),
        responses={
            200: openapi.Response('Курс обновлен', CourseSerializer),
            400: 'Ошибка валидации',
            401: 'Неавторизован',
            403: 'Доступ запрещен',
            404: 'Курс не найден',
        }
    )
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

    @swagger_auto_schema(
        operation_description="Частичное обновление курса",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Название курса'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Описание курса'),
                'preview': openapi.Schema(type=openapi.TYPE_STRING, description='URL превью', nullable=True),
            }
        ),
        responses={
            200: openapi.Response('Курс обновлен', CourseSerializer),
            400: 'Ошибка валидации',
            401: 'Неавторизован',
            403: 'Доступ запрещен',
            404: 'Курс не найден',
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление курса."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Удалить курс",
        responses={
            204: 'Курс удален',
            401: 'Неавторизован',
            403: 'Доступ запрещен (только владелец или администратор)',
            404: 'Курс не найден',
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Удаление курса."""
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        self.perform_destroy(instance)
        return Response(
            {'message': 'Курс успешно удален'},
            status=status.HTTP_204_NO_CONTENT
        )

    def perform_create(self, serializer):
        """При создании курса привязываем владельца"""
        user = self.request.user

        if user.groups.filter(name='moderators').exists():
            raise PermissionDenied("Модераторы не могут создавать курсы")

        serializer.save(owner=user)

    def get_queryset(self):
        """Фильтрация курсов в зависимости от прав"""
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return Course.objects.all()

        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()

        return Course.objects.filter(owner=user)


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

    @swagger_auto_schema(
        operation_description="Получить список всех уроков с пагинацией",
        responses={
            200: LessonDetailSerializer(many=True),
            401: "Неавторизован",
        }
    )
    def get(self, request, *args, **kwargs):
        """Получение списка уроков"""
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создать новый урок",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['course', 'name'],
            properties={
                'course': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID курса'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Название урока'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Описание урока'),
                'preview': openapi.Schema(type=openapi.TYPE_STRING, description='URL превью', nullable=True),
                'video_link': openapi.Schema(type=openapi.TYPE_STRING, description='Ссылка на видео (только YouTube)'),
            }
        ),
        responses={
            201: openapi.Response('Урок создан', LessonSerializer),
            400: 'Ошибка валидации (неверная ссылка или отсутствует курс)',
            401: 'Неавторизован',
            403: 'Доступ запрещен (модераторы не могут создавать уроки)',
        }
    )
    def post(self, request, *args, **kwargs):
        """Создание нового урока"""
        return self.create(request, *args, **kwargs)

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
        """Фильтрация уроков в зависимости от прав"""
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

    @swagger_auto_schema(
        operation_description="Получить детальную информацию об уроке",
        responses={
            200: LessonDetailSerializer(),
            401: 'Неавторизован',
            404: 'Урок не найден',
        }
    )
    def get(self, request, *args, **kwargs):
        """Получение деталей урока"""
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Обновить урок",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'course': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID курса'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Название урока'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Описание урока'),
                'preview': openapi.Schema(type=openapi.TYPE_STRING, description='URL превью', nullable=True),
                'video_link': openapi.Schema(type=openapi.TYPE_STRING, description='Ссылка на видео (только YouTube)'),
            }
        ),
        responses={
            200: openapi.Response('Урок обновлен', LessonSerializer),
            400: 'Ошибка валидации',
            401: 'Неавторизован',
            403: 'Доступ запрещен',
            404: 'Урок не найден',
        }
    )
    def put(self, request, *args, **kwargs):
        """Полное обновление урока"""
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Частичное обновление урока",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'course': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID курса'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Название урока'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Описание урока'),
                'preview': openapi.Schema(type=openapi.TYPE_STRING, description='URL превью', nullable=True),
                'video_link': openapi.Schema(type=openapi.TYPE_STRING, description='Ссылка на видео (только YouTube)'),
            }
        ),
        responses={
            200: openapi.Response('Урок обновлен', LessonSerializer),
            400: 'Ошибка валидации',
            401: 'Неавторизован',
            403: 'Доступ запрещен',
            404: 'Урок не найден',
        }
    )
    def patch(self, request, *args, **kwargs):
        """Частичное обновление урока"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Удалить урок",
        responses={
            204: 'Урок удален',
            401: 'Неавторизован',
            403: 'Доступ запрещен (только владелец или администратор)',
            404: 'Урок не найден',
        }
    )
    def delete(self, request, *args, **kwargs):
        """Удаление урока"""
        return self.destroy(request, *args, **kwargs)

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
