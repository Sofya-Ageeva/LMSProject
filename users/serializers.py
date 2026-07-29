from rest_framework import serializers
from .models import User, Payment
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'city']

    def create(self, validated_data):
        """Создание пользователя с хешированием пароля"""
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            city=validated_data.get('city', '')
        )
        return user

    def validate_email(self, value):
        """Проверка, что email уникален"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User.Преобразует объекты User в JSON и обратно"""

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone',
            'city',
            'avatar',
            'date_joined'
        ]
        read_only_fields = ['date_joined']


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Payment"""

    user_email = serializers.CharField(source='user.email', read_only=True)

    course_name = serializers.CharField(source='paid_course.name', read_only=True, default=None)
    lesson_name = serializers.CharField(source='paid_lesson.name', read_only=True, default=None)

    # Способ оплаты
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'user_email',
            'payment_date',
            'paid_course',
            'course_name',
            'paid_lesson',
            'lesson_name',
            'amount',
            'payment_method',
            'payment_method_display'
        ]
        read_only_fields = ['payment_date']


class UserWithPaymentsSerializer(UserSerializer):
    """Расширенный сериализатор пользователя с историей платежей"""

    payments = PaymentSerializer(many=True, read_only=True)

    total_spent = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['payments', 'total_spent']

    def get_total_spent(self, obj):
        """Возвращает общую сумму всех платежей пользователя"""
        return obj.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
