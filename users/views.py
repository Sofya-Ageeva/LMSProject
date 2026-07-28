from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment
from .serializers import UserSerializer, PaymentSerializer, UserWithPaymentsSerializer
from .filters import PaymentFilter
from django.db import models


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        """Получение деталей о пользователе"""
        if self.action == 'retrieve':
            return UserWithPaymentsSerializer
        return UserSerializer

    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """История платежей выбранного пользователя"""
        user = self.get_object()
        payments = user.payments.select_related('paid_course', 'paid_lesson').all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления платежами. Поддерживает фильтрацию и сортировку."""
    queryset = Payment.objects.select_related('user', 'paid_course', 'paid_lesson').all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter

    def get_queryset(self):
        """Поддержание сортировки через параметр ordering"""
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('ordering')
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset
