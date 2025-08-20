# 🚀 Быстрый старт проекта "Новая Ляда"

## 📋 Требования

- Python 3.12+
- uv (менеджер пакетов)
- Docker и Docker Compose (для продакшена)

## ⚡ Быстрая установка

### 1. Клонирование и настройка

```bash
git clone https://github.com/YOUR_USERNAME/website_about_Novaya_Lyada.git
cd website_about_Novaya_Lyada
```

### 2. Создание виртуального окружения

```bash
uv venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows
```

### 3. Установка зависимостей

```bash
uv pip install -e .
```

### 4. Настройка переменных окружения

```bash
cp env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 5. Запуск проекта

```bash
# Создание и применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Сборка статических файлов
python manage.py collectstatic --noinput

# Запуск сервера разработки
python manage.py runserver
```

## 🐳 Запуск через Docker

### 1. Настройка переменных окружения

```bash
cp env.example .env
# Отредактируйте .env файл
```

### 2. Запуск проекта

```bash
docker compose up -d
```

### 3. Проверка статуса

```bash
docker compose ps
```

## 🔧 Основные команды

```bash
# Django команды
python manage.py runserver          # Запуск сервера разработки
python manage.py migrate            # Применение миграций
python manage.py makemigrations     # Создание миграций
python manage.py collectstatic      # Сборка статических файлов
python manage.py createsuperuser    # Создание админа
python manage.py check --deploy     # Проверка готовности к деплою

# Docker команды
docker compose up -d                # Запуск проекта
docker compose down                 # Остановка проекта
docker compose logs -f web         # Просмотр логов
docker compose ps                  # Статус контейнеров
```

## 📁 Структура проекта

```
website_about_Novaya_Lyada/
├── manage.py                      # Django CLI
├── pyproject.toml                # Конфигурация проекта
├── .env                          # Переменные окружения
├── requirements/                  # Зависимости
├── website_about_novaya_lyada/   # Основной пакет Django
│   ├── settings/                 # Настройки
│   ├── apps/                     # Приложения
│   └── urls.py                   # URL конфигурация
├── static/                       # Статические файлы
├── media/                        # Медиа файлы
├── templates/                    # Шаблоны
└── docker-compose.yml            # Docker конфигурация
```

## 🌐 Доступ к сайту

- **Локальная разработка**: http://localhost:8000/
- **Админ панель**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/

## 📚 Документация

- [Полное руководство по деплою](DEPLOYMENT_GUIDE.md)
- [README](README.md)

## 🆘 Поддержка

При возникновении проблем:
1. Проверьте логи: `python manage.py check --deploy`
2. Убедитесь, что все зависимости установлены
3. Проверьте переменные окружения в `.env`
4. Создайте Issue в GitHub репозитории
