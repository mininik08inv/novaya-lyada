# ⚡ Быстрый старт CI/CD для Новая Ляда

## 🎯 Краткая инструкция по деплою

### 1️⃣ Подготовка сервера (5 минут)

```bash
# На сервере выполните:
sudo bash <(curl -s https://raw.githubusercontent.com/YOUR_USERNAME/website_about_Novaya_Lyada/master/scripts/setup_server.sh)
```

### 2️⃣ Настройка SSH ключей

```bash
# На локальной машине:
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/novaya_lyada

# Копируем публичный ключ на сервер:
ssh-copy-id -i ~/.ssh/novaya_lyada.pub deploy@YOUR_SERVER_IP
```

### 3️⃣ Настройка GitHub Secrets

В настройках репозитория (`Settings > Secrets and variables > Actions`) добавьте:

```
HOST=YOUR_SERVER_IP
USERNAME=deploy
SSH_PRIVATE_KEY=содержимое ~/.ssh/novaya_lyada (приватный ключ)
PORT=22
```

### 4️⃣ Настройка проекта на сервере

```bash
# Подключаемся к серверу
ssh deploy@YOUR_SERVER_IP

# Переходим в директорию проекта
cd /opt/novaya-lyada

# Клонируем репозиторий
git clone https://github.com/YOUR_USERNAME/website_about_Novaya_Lyada.git .

# Создаем .env файл
cp env.production.template .env

# Редактируем .env (заменяем все YOUR_* значения)
nano .env
```

### 5️⃣ Первый деплой

```bash
# Запускаем проект
./scripts/deploy.sh

# Или вручную:
docker-compose up -d

# Проверяем статус
docker-compose ps
curl https://YOUR_DOMAIN/health/
```

### 6️⃣ Готово! 🎉

Теперь при каждом пуше в `master` ветку будет происходить автоматический деплой.

## 📁 Структура файлов

```
website_about_Novaya_Lyada/
├── .github/workflows/deploy.yml    # GitHub Actions CI/CD
├── docker-compose.yml              # Docker Compose конфигурация
├── Dockerfile                      # Docker образ Django
├── docker-entrypoint.sh           # Скрипт запуска контейнера
├── nginx.conf                      # Конфигурация Nginx
├── env.production.template         # Шаблон переменных окружения
├── scripts/
│   ├── setup_server.sh            # Автоматическая настройка сервера
│   ├── deploy.sh                  # Скрипт деплоя
│   ├── backup_db.sh               # Бэкап базы данных
│   └── restore_db.sh              # Восстановление базы данных
└── DEPLOYMENT_GUIDE.md            # Подробное руководство
```

## ⚙️ Основные команды

### На сервере:

```bash
# Статус контейнеров
docker-compose ps

# Логи
docker-compose logs -f web

# Перезапуск
docker-compose restart web

# Деплой
./scripts/deploy.sh

# Бэкап БД
./scripts/backup_db.sh

# Django команды
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### Локально:

```bash
# Разработка с SQLite
cd nl_website
python manage.py runserver

# Тестирование с Docker
docker-compose up -d
```

## 🔧 Конфигурация

### Переменные окружения (.env):

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=0
ALLOWED_HOSTS=your-domain.com

# PostgreSQL
DB_HOST=db
DB_NAME=novaya_lyada
DB_USER=postgres
DB_PASSWORD=strong-password

# OAuth (получить в консолях разработчиков)
GOOGLE_CLIENT_ID=your-google-id
VK_CLIENT_ID=your-vk-id
```

## 🚨 Устранение проблем

### Контейнеры не запускаются:
```bash
docker-compose logs
docker-compose down && docker-compose up -d
```

### Ошибки миграций:
```bash
docker-compose exec web python manage.py showmigrations
docker-compose exec web python manage.py migrate --fake-initial
```

### Проблемы с SSL:
```bash
sudo certbot renew --dry-run
sudo /usr/local/bin/renew-ssl.sh
```

### Нет доступа к сайту:
```bash
# Проверить статус nginx
docker-compose logs nginx

# Проверить брандмауэр
sudo ufw status

# Проверить DNS
nslookup your-domain.com
```

## 📞 Поддержка

- 📚 Подробное руководство: `DEPLOYMENT_GUIDE.md`
- 🐛 Проблемы: создайте Issue в GitHub
- 💬 Вопросы: обратитесь к документации Django/Docker
