from rest_framework import serializers
from .models import User


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