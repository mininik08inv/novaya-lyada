# Используем официальный Python образ
FROM python:3.12-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем uv (быстрый пакетный менеджер Python)
RUN pip install uv

# Устанавливаем зависимости через uv
RUN uv sync --frozen

# Копируем весь проект (НО НЕ .venv!)
COPY . .
RUN rm -rf .venv  # Удаляем скопированное .venv
RUN uv sync --frozen  # Пересоздаем .venv

# Создаем непривилегированного пользователя
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Создаем директории для статических и медиа файлов
RUN mkdir -p /app/staticfiles /app/media

# Открываем порт
EXPOSE 8000

# Создаем скрипт запуска
COPY --chown=appuser:appuser docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Используем скрипт запуска как точку входа
ENTRYPOINT ["/app/docker-entrypoint.sh"]