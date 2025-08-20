# 🚀 Руководство по деплою Django проекта "Новая Ляда"

Подробное руководство по развертыванию Django-сайта на VPS сервер с использованием Docker, PostgreSQL 17 и автоматическим деплоем через GitHub Actions.

## 📋 Содержание

- [Требования](#требования)
- [1. Подготовка VPS сервера](#1-подготовка-vps-сервера)
- [2. Настройка проекта на сервере](#2-настройка-проекта-на-сервере)
- [3. Настройка GitHub Actions](#3-настройка-github-actions)
- [4. Настройка SSL сертификатов](#4-настройка-ssl-сертификатов)
- [5. Первый деплой](#5-первый-деплой)
- [6. Управление проектом](#6-управление-проектом)
- [7. Мониторинг и логи](#7-мониторинг-и-логи)
- [8. Резервное копирование](#8-резервное-копирование)
- [9. Troubleshooting](#9-troubleshooting)

## Требования

- **VPS сервер**: Ubuntu 20.04+ с минимум 2GB RAM, 20GB диска
- **Доменное имя**: например, `novaya-lyada.ru`
- **GitHub репозиторий**: с проектом
- **SSH доступ**: к серверу
- **Базовые знания**: Linux, Docker, Django

## 1. Подготовка VPS сервера

### 1.1 Подключение к серверу

```bash
ssh root@your-server-ip
```

### 1.2 Создание пользователя для деплоя

```bash
# Создаем пользователя deploy
adduser deploy
usermod -aG sudo deploy

# Переключаемся на пользователя deploy
su - deploy
```

### 1.3 Установка Docker и Docker Compose

```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем необходимые пакеты
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Добавляем официальный GPG ключ Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавляем репозиторий Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Устанавливаем Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Добавляем пользователя в группу docker
sudo usermod -aG docker deploy

# Устанавливаем Docker Compose (если не установлен через плагин)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Устанавливаем дополнительные утилиты
sudo apt install -y git nginx certbot python3-certbot-nginx curl wget unzip htop

# Перезагружаемся для применения группы docker
sudo reboot
```

### 1.4 Настройка SSH ключей

На вашем локальном компьютере:

```bash
# Генерируем SSH ключ для GitHub Actions
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions

# Копируем публичный ключ на сервер
ssh-copy-id -i ~/.ssh/github_actions.pub deploy@your-server-ip
```

### 1.5 Настройка брандмауэра

```bash
# Настраиваем UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw status
```

## 2. Настройка проекта на сервере

### 2.1 Создание директории проекта

```bash
# Создаем директорию для проекта
sudo mkdir -p /opt/novaya-lyada
sudo chown deploy:deploy /opt/novaya-lyada
cd /opt/novaya-lyada

# Клонируем репозиторий
git clone https://github.com/YOUR_USERNAME/website_about_Novaya_Lyada.git .

# Создаем файл окружения из шаблона
cp env.example .env
```

### 2.2 Настройка переменных окружения

Отредактируйте файл `.env`:

```bash
nano .env
```

Содержимое файла `.env`:

```bash
# Django settings
SECRET_KEY=your-very-long-and-random-secret-key-here
DEBUG=0
ALLOWED_HOSTS=novaya-lyada.ru,www.novaya-lyada.ru,your-server-ip

# Database settings
DB_HOST=db
DB_NAME=novaya_lyada
DB_USER=postgres
DB_PASSWORD=your-strong-password-here
DB_PORT=5432

# Redis settings
REDIS_URL=redis://redis:6379/0

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@novaya-lyada.ru

# OAuth settings
VK_CLIENT_ID=your-vk-client-id
VK_CLIENT_SECRET=your-vk-client-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Django superuser
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@novaya-lyada.ru
DJANGO_SUPERUSER_PASSWORD=your-admin-password
```

### 2.3 Генерация SECRET_KEY

```bash
# Генерируем SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Копируем сгенерированный ключ в .env файл
nano .env
```

### 2.4 Создание директорий для SSL и логов

```bash
# Создаем директории для SSL сертификатов
mkdir -p ssl

# Создаем директорию для логов
mkdir -p logs

# Создаем директории для статических и медиа файлов
mkdir -p staticfiles media
```

## 3. Настройка GitHub Actions

### 3.1 Создание GitHub Secrets

Перейдите в настройки вашего GitHub репозитория: `Settings > Secrets and variables > Actions`

Создайте следующие секреты:

```
HOST=your-server-ip
USERNAME=deploy
SSH_PRIVATE_KEY=содержимое файла ~/.ssh/github_actions (приватный ключ)
PORT=22
```

### 3.2 Настройка Environment

Создайте environment `production` в GitHub:
`Settings > Environments > New environment`

Добавьте protection rules если нужно (например, требование подтверждения).

### 3.3 Проверка workflow файла

Убедитесь, что файл `.github/workflows/deploy.yml` существует и настроен правильно.

## 4. Настройка SSL сертификатов

### 4.1 Получение SSL сертификата

```bash
# Останавливаем nginx если он запущен
sudo systemctl stop nginx

# Получаем сертификат
sudo certbot certonly --standalone -d novaya-lyada.ru -d www.novaya-lyada.ru

# Копируем сертификаты в проект
sudo cp /etc/letsencrypt/live/novaya-lyada.ru/fullchain.pem /opt/novaya-lyada/ssl/cert.pem
sudo cp /etc/letsencrypt/live/novaya-lyada.ru/privkey.pem /opt/novaya-lyada/ssl/key.pem
sudo chown deploy:deploy /opt/novaya-lyada/ssl/*
```

### 4.2 Настройка автоматического обновления сертификатов

```bash
# Создаем скрипт для обновления сертификатов
sudo tee /usr/local/bin/renew-ssl.sh << 'EOF'
#!/bin/bash
certbot renew --quiet
if [ $? -eq 0 ]; then
    cp /etc/letsencrypt/live/novaya-lyada.ru/fullchain.pem /opt/novaya-lyada/ssl/cert.pem
    cp /etc/letsencrypt/live/novaya-lyada.ru/privkey.pem /opt/novaya-lyada/ssl/key.pem
    chown deploy:deploy /opt/novaya-lyada/ssl/*
    cd /opt/novaya-lyada && docker compose restart nginx
fi
EOF

sudo chmod +x /usr/local/bin/renew-ssl.sh

# Добавляем в crontab
echo "0 3 * * * /usr/local/bin/renew-ssl.sh" | sudo crontab -
```

## 5. Первый деплой

### 5.1 Ручной деплой для проверки

```bash
cd /opt/novaya-lyada

# Проверяем конфигурацию Docker Compose
docker compose config

# Запускаем проект
docker compose up -d

# Проверяем статус
docker compose ps

# Проверяем логи
docker compose logs web
```

### 5.2 Создание суперпользователя

```bash
# Создаем суперпользователя Django
docker compose exec web python manage.py createsuperuser
```

### 5.3 Проверка работы

```bash
# Проверяем доступность
curl http://localhost:8000/

# Проверяем HTTPS (после настройки nginx)
curl https://novaya-lyada.ru/
```

### 5.4 Настройка Nginx

Создайте файл конфигурации Nginx:

```bash
sudo nano /etc/nginx/sites-available/novaya-lyada
```

Содержимое:

```nginx
server {
    listen 80;
    server_name novaya-lyada.ru www.novaya-lyada.ru;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name novaya-lyada.ru www.novaya-lyada.ru;

    ssl_certificate /opt/novaya-lyada/ssl/cert.pem;
    ssl_certificate_key /opt/novaya-lyada/ssl/key.pem;

    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Статические файлы
    location /static/ {
        alias /opt/novaya-lyada/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Медиа файлы
    location /media/ {
        alias /opt/novaya-lyada/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Проксирование к Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активируйте сайт:

```bash
sudo ln -s /etc/nginx/sites-available/novaya-lyada /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 6. Управление проектом

### 6.1 Основные команды Docker Compose

```bash
# Просмотр статуса
docker compose ps

# Просмотр логов
docker compose logs -f web
docker compose logs -f db
docker compose logs -f nginx

# Перезапуск сервисов
docker compose restart web
docker compose restart nginx

# Остановка проекта
docker compose down

# Запуск проекта
docker compose up -d

# Пересборка проекта
docker compose build --no-cache
docker compose up -d
```

### 6.2 Django команды

```bash
# Выполнение миграций
docker compose exec web python manage.py migrate

# Сборка статических файлов
docker compose exec web python manage.py collectstatic --noinput

# Создание суперпользователя
docker compose exec web python manage.py createsuperuser

# Проверка проекта
docker compose exec web python manage.py check --deploy

# Shell Django
docker compose exec web python manage.py shell
```

### 6.3 Управление базой данных

```bash
# Доступ к базе данных
docker compose exec db psql -U postgres -d novaya_lyada

# Создание бэкапа
docker compose exec db pg_dump -U postgres novaya_lyada > backup.sql

# Восстановление из бэкапа
docker compose exec -T db psql -U postgres novaya_lyada < backup.sql
```

### 6.4 Использование скриптов

```bash
# Автоматический деплой
./scripts/deploy.sh

# Создание бэкапа БД
./scripts/backup_db.sh

# Восстановление БД
./scripts/restore_db.sh ./backups/backup_20240101_120000.sql.gz

# Настройка сервера
./scripts/setup_server.sh
```

## 7. Мониторинг и логи

### 7.1 Настройка логирования

```bash
# Настройка ротации логов Docker
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

sudo systemctl restart docker
```

### 7.2 Мониторинг ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Использование диска
df -h
docker system df

# Очистка неиспользуемых данных
docker system prune -f
docker volume prune -f
```

### 7.3 Просмотр логов

```bash
# Логи Django приложения
docker compose logs -f web

# Логи базы данных
docker compose logs -f db

# Логи Redis
docker compose logs -f redis

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 8. Резервное копирование

### 8.1 Автоматическое создание бэкапов

```bash
# Создаем скрипт ежедневного бэкапа
sudo tee /usr/local/bin/daily-backup.sh << 'EOF'
#!/bin/bash
cd /opt/novaya-lyada

# Создаем директорию для бэкапов если её нет
mkdir -p backups

# Бэкап базы данных
docker compose exec -T db pg_dump -U postgres novaya_lyada | gzip > ./backups/db_$(date +%Y%m%d_%H%M%S).sql.gz

# Бэкап медиа файлов
tar -czf ./backups/media_$(date +%Y%m%d_%H%M%S).tar.gz media/

# Бэкап .env файла
cp .env ./backups/env_$(date +%Y%m%d_%H%M%S).backup

# Удаляем старые бэкапы (старше 30 дней)
find ./backups -name "*.gz" -mtime +30 -delete
find ./backups -name "*.backup" -mtime +30 -delete
find ./backups -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $(date)" >> ./backups/backup.log
EOF

sudo chmod +x /usr/local/bin/daily-backup.sh

# Добавляем в crontab (каждый день в 2:00)
echo "0 2 * * * /usr/local/bin/daily-backup.sh" >> /tmp/crontab
crontab /tmp/crontab
```

### 8.2 Ручное создание бэкапов

```bash
# Бэкап базы данных
cd /opt/novaya-lyada
docker compose exec -T db pg_dump -U postgres novaya_lyada | gzip > ./backups/manual_backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Бэкап медиа файлов
tar -czf ./backups/manual_media_$(date +%Y%m%d_%H%M%S).tar.gz media/

# Бэкап всего проекта
tar -czf ./backups/full_project_$(date +%Y%m%d_%H%M%S).tar.gz --exclude='.git' --exclude='.venv' --exclude='backups' .
```

### 8.3 Восстановление из бэкапа

```bash
# Восстановление базы данных
cd /opt/opt/novaya-lyada
gunzip -c ./backups/db_20240101_120000.sql.gz | docker compose exec -T db psql -U postgres novaya_lyada

# Восстановление медиа файлов
tar -xzf ./backups/media_20240101_120000.tar.gz

# Восстановление .env файла
cp ./backups/env_20240101_120000.backup .env
```

## 9. Troubleshooting

### 9.1 Частые проблемы

#### Проблема: Контейнеры не запускаются
```bash
# Проверяем логи
docker compose logs

# Проверяем конфигурацию
docker compose config

# Проверяем переменные окружения
cat .env
```

#### Проблема: База данных недоступна
```bash
# Проверяем статус контейнера БД
docker compose ps db

# Проверяем логи БД
docker compose logs db

# Проверяем подключение
docker compose exec web python manage.py dbshell
```

#### Проблема: Статические файлы не загружаются
```bash
# Собираем статические файлы
docker compose exec web python manage.py collectstatic --noinput

# Проверяем права доступа
ls -la staticfiles/
```

#### Проблема: SSL сертификат истек
```bash
# Обновляем сертификат вручную
sudo certbot renew

# Копируем новые сертификаты
sudo cp /etc/letsencrypt/live/novaya-lyada.ru/fullchain.pem /opt/novaya-lyada/ssl/cert.pem
sudo cp /etc/letsencrypt/live/novaya-lyada.ru/privkey.pem /opt/novaya-lyada/ssl/key.pem
sudo chown deploy:deploy /opt/novaya-lyada/ssl/*

# Перезапускаем nginx
sudo systemctl restart nginx
```

### 9.2 Полезные команды для диагностики

```bash
# Проверка использования портов
sudo netstat -tlnp

# Проверка статуса сервисов
sudo systemctl status nginx
sudo systemctl status docker

# Проверка дискового пространства
df -h
du -sh /opt/novaya-lyada/*

# Проверка памяти
free -h
htop

# Проверка логов системы
sudo journalctl -u nginx -f
sudo journalctl -u docker -f
```

### 9.3 Восстановление после сбоя

```bash
# Полная перезагрузка проекта
cd /opt/novaya-lyada
docker compose down
docker compose up -d

# Проверка статуса
docker compose ps

# Проверка логов
docker compose logs
```

## 🎉 Готово!

После выполнения всех шагов у вас будет:

- ✅ Автоматический деплой при пуше в master ветку
- ✅ Docker-контейнеры с PostgreSQL 17, Redis, Nginx
- ✅ SSL сертификаты с автоматическим обновлением
- ✅ Автоматические бэкапы базы данных и медиа файлов
- ✅ Мониторинг и логирование
- ✅ Готовая к продакшену инфраструктура

## 🔧 Поддержка

Если у вас возникли проблемы:

1. **Проверьте логи**: `docker compose logs web`
2. **Проверьте статус**: `docker compose ps`
3. **Проверьте доступность**: `curl http://localhost:8000/`
4. **Проверьте переменные окружения**: `cat .env`
5. **Проверьте SSL сертификаты**: `sudo certbot certificates`

## 📚 Дополнительные ресурсы

- [Документация Docker](https://docs.docker.com/)
- [Документация Django](https://docs.djangoproject.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Nginx конфигурация](https://nginx.org/en/docs/)
- [PostgreSQL документация](https://www.postgresql.org/docs/)
- [Let's Encrypt документация](https://letsencrypt.org/docs/)

## 📞 Контакты

При возникновении вопросов или проблем:
- Создайте Issue в GitHub репозитории
- Обратитесь к документации Django
- Проверьте логи и статус сервисов
