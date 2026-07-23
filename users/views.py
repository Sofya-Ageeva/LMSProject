from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.
    Предоставляет все CRUD операции:
    - GET /users/ - список пользователей
    - POST /users/ - создание пользователя
    - GET /users/{id}/ - получение пользователя
    - PUT /users/{id}/ - полное обновление
    - PATCH /users/{id}/ - частичное обновление
    - DELETE /users/{id}/ - удаление пользователя
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

