import re
from rest_framework.exceptions import ValidationError


def validate_youtube_url(value):
    """Валидатор проверяет, что ссылка ведет на youtube.com"""
    if not value:
        return value

    youtube_pattern = re.compile(
        r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$'
    )

    if not youtube_pattern.match(value):
        raise ValidationError(
            'Разрешены только ссылки на YouTube. '
            'Пожалуйста, используйте ссылки вида: '
            'https://www.youtube.com/watch?v=... или https://youtu.be/...'
        )

    return value