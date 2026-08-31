# LMS-Project

Сервис для онлайн-обучения с курсами, уроками, подписками и платежами.

## Функционал

- Регистрация и JWT-авторизация
- CRUD пользователей, курсов, уроков
- Подписка на обновления курсов
- Уведомления подписчикам (Celery)
- Оплата через Stripe
- Валидация YouTube ссылок
- Пагинация
- Права доступа (модераторы, владельцы)
- Документация Swagger/ReDoc


## Запуск через Docker

```bash
# 1. Клонирование репозитория
git clone https://github.com/Sofya-Ageeva/LMSProject.git
cd LMSProject

# 2. Создание .env из шаблона
cp .env.template .env
# Заполни .env своими данными

# 3. Запуск контейнеров
docker compose up -d --build

# 4. Применение миграций
docker compose exec web python manage.py migrate

# 5. Создание суперпользователя
docker compose exec web python manage.py createsuperuser