from rest_framework import viewsets, filters, status, generics
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from materials.models import Course
from .models import User, Payment, Subscription
from .serializers import (
    UserSerializer, PaymentSerializer, SubscriptionSerializer, UserRegistrationSerializer, PrivateUserSerializer,
    PublicUserSerializer)
from .filters import PaymentFilter
from django.db import models
from .permissions import IsModerator, IsOwnerOrAdmin, IsOwnerOrReadOnly

class UserRegistrationView(generics.CreateAPIView):
    """Регистрация нового пользователя. Доступ для всех (неавторизованных)"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Разные права для разных действий"""
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'update' or self.action == 'partial_update':
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        """Получение деталей о пользователе"""
        if self.action == 'retrieve':
            user = self.get_object()
            if user == self.request.user:
                return PrivateUserSerializer
            return PublicUserSerializer
        return UserSerializer

    def get_queryset(self):
        """Ограничиваем доступ к списку пользователей"""
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """История платежей выбранного пользователя"""
        user = self.get_object()
        if request.user != user and not request.user.is_superuser:
            return Response(
                {'detail': 'У вас нет доступа для просмотра данных этого пользователя'},
                status=status.HTTP_403_FORBIDDEN
            )
        payments = user.payments.select_related('paid_course', 'paid_lesson').all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления платежами. Поддерживает фильтрацию и сортировку."""
    queryset = Payment.objects.select_related('user', 'paid_course', 'paid_lesson').all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Разные права для разных действий"""
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'update' or self.action == 'partial_update':
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """Привязка данных о платежах его к текущему пользователю"""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Фильтрация платежей по пользователю"""
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(user=user)


class SubscriptionView(APIView):
    """
    Управление подпиской на курс
    POST: создает или удаляет подписку
    GET: проверяет статус подписки
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Создание или удаление подписки"""
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {'error': 'Необходимо указать course_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)

        subscription = Subscription.objects.filter(
            user=user,
            course=course
        ).first()

        if subscription:
            subscription.delete()
            message = 'Подписка удалена'
            is_subscribed = False
        else:
            subscription = Subscription.objects.create(
                user=user,
                course=course
            )
            message = 'Подписка добавлена'
            is_subscribed = True

        return Response({
            'message': message,
            'is_subscribed': is_subscribed,
            'course_id': course.id,
            'course_name': course.name
        }, status=status.HTTP_200_OK)

    def get(self, request):
        """Проверка статуса подписки"""
        user = request.user
        course_id = request.query_params.get('course_id')

        if not course_id:
            return Response(
                {'error': 'Необходимо указать course_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)
        is_subscribed = Subscription.objects.filter(
            user=user,
            course=course
        ).exists()

        return Response({
            'is_subscribed': is_subscribed,
            'course_id': course.id,
            'course_name': course.name
        })
