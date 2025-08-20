# 🚀 Руководство по настройке CI/CD и деплою на VPS

Это руководство поможет вам настроить автоматический деплой Django-сайта "Новая Ляда" на VPS сервер с использованием GitHub Actions, Docker и PostgreSQL 17.

## 📋 Содержание

- [Требования](#требования)
- [1. Настройка VPS сервера](#1-настройка-vps-сервера)
- [2. Настройка GitHub Actions](#2-настройка-github-actions)
- [3. Настройка SSL сертификатов](#3-настройка-ssl-сертификатов)
- [4. Первый деплой](#4-первый-деплой)
- [5. Управление проектом](#5-управление-проектом)
- [6. Мониторинг и логи](#6-мониторинг-и-логи)
- [7. Резервное копирование](#7-резервное-копирование)

## Требования

- VPS сервер на Ubuntu 20.04+ с минимум 2GB RAM
- Доменное имя (например, novaya-lyada.ru)
- GitHub репозиторий с проектом
- SSH доступ к серверу

## 1. Настройка VPS сервера

### 1.1 Подключение к серверу

```bash
ssh root@your-server-ip
```

### 1.2 Создание пользователя для деплоя

```bash
# Создаем пользователя deploy
adduser deploy
usermod -aG sudo deploy
usermod -aG docker deploy

# Переключаемся на пользователя deploy
su - deploy
```

### 1.3 Установка необходимого ПО

```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Устанавливаем Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Устанавливаем дополнительные утилиты
sudo apt install -y git nginx certbot python3-certbot-nginx curl wget unzip

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

### 1.5 Создание директории проекта

```bash
# Создаем директорию для проекта
sudo mkdir -p /opt/novaya-lyada
sudo chown deploy:deploy /opt/novaya-lyada
cd /opt/novaya-lyada

# Клонируем репозиторий
git clone https://github.com/YOUR_USERNAME/website_about_Novaya_Lyada.git .

# Создаем файл окружения из шаблона
cp env.production.template .env

# Редактируем файл окружения
nano .env
```

### 1.6 Настройка окружения

Отредактируйте файл `.env`, заменив все значения на реальные:

```bash
# Генерируем SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Используйте полученный ключ в .env файле
SECRET_KEY=your-generated-secret-key
DEBUG=0
ALLOWED_HOSTS=novaya-lyada.ru,www.novaya-lyada.ru

# Настройте остальные параметры согласно шаблону
```

### 1.7 Настройка брандмауэра

```bash
# Настраиваем UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw status
```

## 2. Настройка GitHub Actions

### 2.1 Создание GitHub Secrets

Перейдите в настройки вашего GitHub репозитория: `Settings > Secrets and variables > Actions`

Создайте следующие секреты:

```
HOST=your-server-ip
USERNAME=deploy
SSH_PRIVATE_KEY=содержимое файла ~/.ssh/github_actions (приватный ключ)
PORT=22
```

### 2.2 Настройка Environment

Создайте environment `production` в GitHub:
`Settings > Environments > New environment`

Добавьте protection rules если нужно (например, требование подтверждения).

## 3. Настройка SSL сертификатов

### 3.1 Получение SSL сертификата

```bash
# Останавливаем nginx если он запущен
sudo systemctl stop nginx

# Получаем сертификат
sudo certbot certonly --standalone -d novaya-lyada.ru -d www.novaya-lyada.ru

# Создаем директорию для SSL в проекте
mkdir -p /opt/novaya-lyada/ssl

# Копируем сертификаты
sudo cp /etc/letsencrypt/live/novaya-lyada.ru/fullchain.pem /opt/novaya-lyada/ssl/cert.pem
sudo cp /etc/letsencrypt/live/novaya-lyada.ru/privkey.pem /opt/novaya-lyada/ssl/key.pem
sudo chown deploy:deploy /opt/novaya-lyada/ssl/*
```

### 3.2 Настройка автоматического обновления сертификатов

```bash
# Создаем скрипт для обновления сертификатов
sudo tee /usr/local/bin/renew-ssl.sh << 'EOF'
#!/bin/bash
certbot renew --quiet
if [ $? -eq 0 ]; then
    cp /etc/letsencrypt/live/novaya-lyada.ru/fullchain.pem /opt/novaya-lyada/ssl/cert.pem
    cp /etc/letsencrypt/live/novaya-lyada.ru/privkey.pem /opt/novaya-lyada/ssl/key.pem
    chown deploy:deploy /opt/novaya-lyada/ssl/*
    cd /opt/novaya-lyada && docker-compose restart nginx
fi
EOF

sudo chmod +x /usr/local/bin/renew-ssl.sh

# Добавляем в crontab
echo "0 3 * * * /usr/local/bin/renew-ssl.sh" | sudo crontab -
```

## 4. Первый деплой

### 4.1 Ручной деплой для проверки

```bash
cd /opt/novaya-lyada

# Создаем .env файл если еще не создан
cp env.production.template .env
# Отредактируйте .env файл с реальными данными

# Запускаем проект
docker-compose up -d

# Проверяем статус
docker-compose ps

# Проверяем логи
docker-compose logs web
```

### 4.2 Создание суперпользователя

```bash
# Создаем суперпользователя Django
docker-compose exec web python manage.py createsuperuser
```

### 4.3 Проверка работы

```bash
# Проверяем доступность
curl http://localhost/health/

# Проверяем HTTPS
curl https://novaya-lyada.ru/health/
```

## 5. Управление проектом

### 5.1 Основные команды

```bash
# Просмотр статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f web
docker-compose logs -f db

# Перезапуск сервисов
docker-compose restart web
docker-compose restart nginx

# Выполнение Django команд
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput

# Доступ к базе данных
docker-compose exec db psql -U postgres -d novaya_lyada
```

### 5.2 Использование скриптов

```bash
# Автоматический деплой
./scripts/deploy.sh

# Создание бэкапа БД
./scripts/backup_db.sh

# Восстановление БД
./scripts/restore_db.sh ./backups/backup_20240101_120000.sql.gz
```

## 6. Мониторинг и логи

### 6.1 Настройка логирования

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

### 6.2 Мониторинг ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Использование диска
df -h
docker system df

# Очистка неиспользуемых данных
docker system prune -f
```

## 7. Резервное копирование

### 7.1 Автоматическое создание бэкапов

```bash
# Создаем скрипт ежедневного бэкапа
sudo tee /usr/local/bin/daily-backup.sh << 'EOF'
#!/bin/bash
cd /opt/novaya-lyada
./scripts/backup_db.sh

# Бэкап медиа файлов
tar -czf ./backups/media_$(date +%Y%m%d_%H%M%S).tar.gz nl_website/media/

# Удаляем старые бэкапы (старше 30 дней)
find ./backups -name "*.gz" -mtime +30 -delete
EOF

sudo chmod +x /usr/local/bin/daily-backup.sh

# Добавляем в crontab (каждый день в 2:00)
echo "0 2 * * * /usr/local/bin/daily-backup.sh" | sudo crontab -
```

### 7.2 Настройка удаленного бэкапа (опционально)

```bash
# Установка rclone для загрузки в облако
curl https://rclone.org/install.sh | sudo bash

# Настройка (следуйте инструкциям)
rclone config

# Добавление в скрипт бэкапа загрузки в облако
echo "rclone copy ./backups/ remote:novaya-lyada-backups/" >> /usr/local/bin/daily-backup.sh
```

## 🎉 Готово!

После выполнения всех шагов у вас будет:

- ✅ Автоматический деплой при пуше в master ветку
- ✅ Docker-контейнеры с PostgreSQL 17, Redis, Nginx
- ✅ SSL сертификаты с автоматическим обновлением
- ✅ Автоматические бэкапы базы данных
- ✅ Мониторинг и логирование
- ✅ Готовая к продакшену инфраструктура

## 🔧 Поддержка

Если у вас возникли проблемы:

1. Проверьте логи: `docker-compose logs web`
2. Проверьте статус контейнеров: `docker-compose ps`
3. Проверьте доступность: `curl http://localhost/health/`
4. Проверьте переменные окружения в `.env` файле

## 📚 Дополнительные ресурсы

- [Документация Docker](https://docs.docker.com/)
- [Документация Django](https://docs.djangoproject.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Nginx конфигурация](https://nginx.org/en/docs/)
- [PostgreSQL документация](https://www.postgresql.org/docs/)
