#!/bin/bash
set -e

# Функция для ожидания готовности базы данных
wait_for_db() {
    echo "Waiting for PostgreSQL..."
    while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
        sleep 1
    done
    echo "PostgreSQL is ready!"
}

# Активируем виртуальное окружение uv
source /app/.venv/bin/activate

# Гарантируем продакшен-настройки по умолчанию в контейнере
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
    export DJANGO_SETTINGS_MODULE=website_about_novaya_lyada.settings.production
fi

# Ждем готовности базы данных
if [ "$DB_HOST" ]; then
    wait_for_db
fi

# Выполняем миграции
echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Собираем статические файлы
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Создаем суперпользователя, если он не существует
echo "Creating superuser if it doesn't exist..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@novaya-lyada.ru')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} created')
else:
    print(f'Superuser {username} already exists')
EOF

# Запускаем команду переданную в аргументах или Gunicorn по умолчанию
if [ "$1" = "runserver" ]; then
    echo "Starting Django development server..."
    exec python manage.py runserver 0.0.0.0:8000
elif [ "$1" = "celery" ]; then
    echo "Starting Celery worker..."
    exec celery -A website_about_novaya_lyada worker --loglevel=info
elif [ "$1" = "celerybeat" ]; then
    echo "Starting Celery beat..."
    exec celery -A website_about_novaya_lyada beat --loglevel=info
else
    echo "Starting Gunicorn..."
    exec gunicorn website_about_novaya_lyada.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 3 \
        --timeout 30 \
        --keep-alive 2 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --access-logfile - \
        --error-logfile -
fi
