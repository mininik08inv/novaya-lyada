#!/bin/bash

# Скрипт для полного развертывания проекта на сервере
# Запускать на сервере в директории /opt/novaya-lyada

set -e

echo "🚀 Развертывание проекта 'Новая Ляда' на сервере..."
echo "=================================================="

# Проверяем, что мы в правильной директории
if [ ! -f "manage.py" ]; then
    echo "❌ Ошибка: manage.py не найден. Запустите скрипт из корня проекта."
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "❌ Ошибка: .env файл не найден."
    echo "📝 Создайте .env файл из env.example:"
    echo "   cp env.example .env"
    echo "   nano .env"
    exit 1
fi

# Проверяем Docker
echo "🐳 Проверка Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и Docker Compose."
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose."
    exit 1
fi

echo "✅ Docker и Docker Compose доступны"

# Создаем необходимые директории
echo "📁 Создание необходимых директорий..."
mkdir -p staticfiles media logs ssl backups

# Проверяем права доступа
echo "🔐 Установка правильных прав доступа..."
chmod 644 .env
chmod +x scripts/*.sh 2>/dev/null || true

# Останавливаем существующие контейнеры если они запущены
echo "🛑 Остановка существующих контейнеров..."
docker compose down 2>/dev/null || true

# Удаляем старые образы
echo "🧹 Очистка старых образов..."
docker image prune -f 2>/dev/null || true

# Собираем и запускаем проект
echo "🔨 Сборка и запуск проекта..."
docker compose build --no-cache
docker compose up -d

# Ждем запуска контейнеров
echo "⏳ Ожидание запуска контейнеров..."
sleep 10

# Проверяем статус
echo "📊 Статус контейнеров:"
docker compose ps

# Проверяем логи
echo "📋 Проверка логов..."
docker compose logs --tail=20

# Ждем готовности приложения
echo "⏳ Ожидание готовности приложения..."
for i in {1..30}; do
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        echo "✅ Приложение готово!"
        break
    fi
    echo "⏳ Ожидание... ($i/30)"
    sleep 10
done

# Выполняем Django команды
echo "🐍 Выполнение Django команд..."

# Применяем миграции
echo "📦 Применение миграций..."
docker compose exec -T web python manage.py migrate --noinput

# Собираем статические файлы
echo "🎨 Сборка статических файлов..."
docker compose exec -T web python manage.py collectstatic --noinput

# Проверяем проект
echo "🔍 Проверка проекта..."
docker compose exec -T web python manage.py check --deploy

# Создаем суперпользователя если его нет
echo "👤 Проверка суперпользователя..."
if ! docker compose exec -T web python manage.py shell -c "from django.contrib.auth.models import User; print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')" 2>/dev/null | grep -q "Superuser exists"; then
    echo "⚠️  Суперпользователь не найден. Создайте его вручную:"
    echo "   docker compose exec web python manage.py createsuperuser"
else
    echo "✅ Суперпользователь существует"
fi

# Создаем бэкап
echo "💾 Создание бэкапа..."
mkdir -p backups
docker compose exec -T db pg_dump -U postgres novaya_lyada > ./backups/deploy_backup_$(date +%Y%m%d_%H%M%S).sql 2>/dev/null || echo "⚠️  Не удалось создать бэкап БД"

# Финальная проверка
echo "🎯 Финальная проверка..."
echo "=================================="
echo "📊 Статус контейнеров:"
docker compose ps

echo ""
echo "🌐 Доступность приложения:"
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ HTTP: http://localhost:8000/"
else
    echo "❌ HTTP: недоступно"
fi

echo ""
echo "📁 Структура проекта:"
tree -d -L 2 2>/dev/null || find . -type d | head -20

echo ""
echo "🎉 Развертывание завершено!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Настройте Nginx для проксирования на порт 8000"
echo "2. Настройте SSL сертификаты"
echo "3. Создайте суперпользователя если нужно:"
echo "   docker compose exec web python manage.py createsuperuser"
echo ""
echo "🔧 Полезные команды:"
echo "   docker compose ps                    # Статус контейнеров"
echo "   docker compose logs -f web          # Логи веб-приложения"
echo "   docker compose logs -f db           # Логи базы данных"
echo "   docker compose restart web          # Перезапуск веб-приложения"
echo "   docker compose down                 # Остановка проекта"
echo "   docker compose up -d                # Запуск проекта"
