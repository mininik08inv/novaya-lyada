#!/bin/bash
set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo -e "${RED}❌ Usage: $0 <backup_file.sql.gz>${NC}"
    echo -e "${YELLOW}Available backups:${NC}"
    ls -la ./backups/backup_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}🔄 Restoring database from: $BACKUP_FILE${NC}"

# Проверяем, что база данных запущена
if ! docker-compose ps db | grep -q "Up"; then
    echo -e "${RED}❌ Database container is not running. Please start it first with: docker-compose up -d db${NC}"
    exit 1
fi

# Создаем временный файл для распакованного SQL
TEMP_SQL="/tmp/restore_$(date +%Y%m%d_%H%M%S).sql"

# Распаковываем бэкап
echo -e "${YELLOW}📤 Extracting backup...${NC}"
gunzip -c "$BACKUP_FILE" > "$TEMP_SQL"

# Останавливаем веб-приложение для безопасности
echo -e "${YELLOW}⏹️  Stopping web application...${NC}"
docker-compose stop web celery celerybeat

# Восстанавливаем базу данных
echo -e "${YELLOW}🔄 Restoring database...${NC}"
docker-compose exec -T db psql -U postgres -d novaya_lyada < "$TEMP_SQL"

# Удаляем временный файл
rm "$TEMP_SQL"

# Запускаем веб-приложение
echo -e "${YELLOW}▶️  Starting web application...${NC}"
docker-compose up -d web celery celerybeat

echo -e "${GREEN}✅ Database restored successfully from: $BACKUP_FILE${NC}"
