#!/bin/bash
set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}📦 Creating database backup...${NC}"

# Создаем директорию для бэкапов
mkdir -p ./backups

# Генерируем имя файла с датой и временем
BACKUP_FILE="./backups/backup_$(date +%Y%m%d_%H%M%S).sql"

# Создаем бэкап
docker-compose exec -T db pg_dump -U postgres -h localhost novaya_lyada > "$BACKUP_FILE"

# Сжимаем бэкап
gzip "$BACKUP_FILE"

echo -e "${GREEN}✅ Database backup created: ${BACKUP_FILE}.gz${NC}"

# Удаляем старые бэкапы (старше 30 дней)
find ./backups -name "backup_*.sql.gz" -mtime +30 -delete
echo -e "${GREEN}🧹 Old backups (older than 30 days) have been removed${NC}"
