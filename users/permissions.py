from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверка на права модератора"""

    def has_permission(self, request, view):
        """Проверка для всего запроса"""
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='moderators').exists()

    def has_object_permission(self, request, view, obj):
        """Проверка для конкретного объекта"""
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(permissions.BasePermission):
    """Проверка статуса владельца объекта"""

    def has_object_permission(self, request, view, obj):
        """Проверка для конкретного объекта"""
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsOwnerOrModerator(permissions.BasePermission):
    """Проверка пользователя на статус владельца или модератора"""

    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='moderators').exists():
            return True
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Проверка прав доступа пользователя"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """Проверка пользователя на статус владельца или администратора"""

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False
