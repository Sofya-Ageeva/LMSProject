from rest_framework import viewsets, filters, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment
from .serializers import (
    UserSerializer, PaymentSerializer, UserWithPaymentsSerializer, UserRegistrationSerializer)
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
            return UserWithPaymentsSerializer
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
