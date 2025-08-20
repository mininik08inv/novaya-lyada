# Website About Novaya Lyada

Веб-сайт о селе Новая Ляда Тамбовской области.

## Структура проекта

```
website_about_novaya_lyada/          # Главный пакет проекта
├── settings/                         # Настройки Django
│   ├── base.py                      # Базовые настройки
│   ├── development.py               # Настройки для разработки
│   └── production.py                # Настройки для продакшена
├── apps/                            # Приложения Django
│   ├── core/                        # Основное приложение
│   ├── accounts/                    # Управление пользователями
│   ├── ideas/                       # Идеи и предложения
│   ├── about_village/               # Информация о селе
│   ├── advertisement/               # Объявления
│   ├── places/                      # Места
│   └── events/                      # События
├── urls.py                          # Основные URL
├── wsgi.py                          # WSGI конфигурация
├── asgi.py                          # ASGI конфигурация
└── celery.py                        # Celery конфигурация
```

## Установка и запуск

### Требования
- Python 3.12+
- uv (менеджер пакетов)

### Установка зависимостей
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Настройка переменных окружения
```bash
cp env.example .env
# Отредактируйте .env файл с вашими настройками
```

### Запуск сервера разработки
```bash
python manage.py runserver
```

### Применение миграций
```bash
python manage.py migrate
```

### Создание суперпользователя
```bash
python manage.py createsuperuser
```

## Разработка

Проект использует современную структуру Django с разделением настроек для разработки и продакшена.

### Структура настроек
- `settings/base.py` - общие настройки
- `settings/development.py` - настройки для разработки
- `settings/production.py` - настройки для продакшена

### Приложения
Все приложения находятся в папке `apps/` и следуют стандартной структуре Django.

## Деплой

Для деплоя используйте Docker Compose:

```bash
docker-compose up -d
```

Подробная инструкция по деплою находится в файле `DEPLOYMENT_GUIDE.md`.
