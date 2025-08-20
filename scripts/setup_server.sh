#!/bin/bash
set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Novaya Lyada Server Setup Script${NC}"
echo -e "${BLUE}====================================${NC}"

# Проверяем, что скрипт запущен с правами sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

# Получаем информацию от пользователя
echo -e "${YELLOW}📝 Please provide the following information:${NC}"
read -p "Domain name (e.g., novaya-lyada.ru): " DOMAIN
read -p "Email for SSL certificate: " EMAIL
read -p "Deploy user name (default: deploy): " DEPLOY_USER
DEPLOY_USER=${DEPLOY_USER:-deploy}

echo -e "${GREEN}🔧 Starting server setup...${NC}"

# Обновляем систему
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update && apt upgrade -y

# Устанавливаем необходимые пакеты
echo -e "${YELLOW}📦 Installing required packages...${NC}"
apt install -y curl wget git nginx certbot python3-certbot-nginx ufw fail2ban htop

# Создаем пользователя deploy
echo -e "${YELLOW}👤 Creating deploy user...${NC}"
if ! id "$DEPLOY_USER" &>/dev/null; then
    adduser --disabled-password --gecos "" $DEPLOY_USER
    usermod -aG sudo $DEPLOY_USER
    echo -e "${GREEN}✅ User $DEPLOY_USER created${NC}"
else
    echo -e "${YELLOW}⚠️  User $DEPLOY_USER already exists${NC}"
fi

# Устанавливаем Docker
echo -e "${YELLOW}🐳 Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    usermod -aG docker $DEPLOY_USER
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${YELLOW}⚠️  Docker already installed${NC}"
fi

# Устанавливаем Docker Compose
echo -e "${YELLOW}🐳 Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
else
    echo -e "${YELLOW}⚠️  Docker Compose already installed${NC}"
fi

# Настраиваем брандмауэр
echo -e "${YELLOW}🔥 Configuring firewall...${NC}"
ufw --force enable
ufw allow ssh
ufw allow 80
ufw allow 443
ufw status

# Настраиваем fail2ban
echo -e "${YELLOW}🔒 Configuring fail2ban...${NC}"
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
systemctl enable fail2ban
systemctl start fail2ban

# Создаем директорию проекта
echo -e "${YELLOW}📁 Creating project directory...${NC}"
mkdir -p /opt/novaya-lyada
chown $DEPLOY_USER:$DEPLOY_USER /opt/novaya-lyada

# Получаем SSL сертификат
echo -e "${YELLOW}🔐 Obtaining SSL certificate...${NC}"
systemctl stop nginx
if certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive; then
    echo -e "${GREEN}✅ SSL certificate obtained${NC}"
    
    # Создаем директорию для SSL в проекте
    mkdir -p /opt/novaya-lyada/ssl
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/novaya-lyada/ssl/cert.pem
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/novaya-lyada/ssl/key.pem
    chown $DEPLOY_USER:$DEPLOY_USER /opt/novaya-lyada/ssl/*
else
    echo -e "${RED}❌ Failed to obtain SSL certificate. Please check domain configuration.${NC}"
fi

# Создаем скрипт обновления сертификатов
echo -e "${YELLOW}🔄 Setting up SSL renewal...${NC}"
cat > /usr/local/bin/renew-ssl.sh << EOF
#!/bin/bash
certbot renew --quiet
if [ \$? -eq 0 ]; then
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/novaya-lyada/ssl/cert.pem
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/novaya-lyada/ssl/key.pem
    chown $DEPLOY_USER:$DEPLOY_USER /opt/novaya-lyada/ssl/*
    cd /opt/novaya-lyada && docker-compose restart nginx
fi
EOF
chmod +x /usr/local/bin/renew-ssl.sh

# Добавляем в crontab
echo "0 3 * * * /usr/local/bin/renew-ssl.sh" | crontab -

# Создаем скрипт ежедневного бэкапа
echo -e "${YELLOW}💾 Setting up daily backup...${NC}"
cat > /usr/local/bin/daily-backup.sh << EOF
#!/bin/bash
cd /opt/novaya-lyada
if [ -f "./scripts/backup_db.sh" ]; then
    sudo -u $DEPLOY_USER ./scripts/backup_db.sh
    
    # Бэкап медиа файлов
    sudo -u $DEPLOY_USER tar -czf ./backups/media_\$(date +%Y%m%d_%H%M%S).tar.gz nl_website/media/ 2>/dev/null || true
    
    # Удаляем старые бэкапы (старше 30 дней)
    find ./backups -name "*.gz" -mtime +30 -delete 2>/dev/null || true
fi
EOF
chmod +x /usr/local/bin/daily-backup.sh

# Добавляем в crontab (каждый день в 2:00)
echo "0 2 * * * /usr/local/bin/daily-backup.sh" | crontab -

# Настраиваем логирование Docker
echo -e "${YELLOW}📝 Configuring Docker logging...${NC}"
cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# Создаем файл с информацией о настройке
cat > /opt/novaya-lyada/SERVER_INFO.txt << EOF
Novaya Lyada Server Setup Complete
==================================

Domain: $DOMAIN
Deploy User: $DEPLOY_USER
Project Directory: /opt/novaya-lyada
SSL Certificates: /etc/letsencrypt/live/$DOMAIN/

Next Steps:
1. Copy SSH public key for deploy user
2. Clone repository to /opt/novaya-lyada
3. Configure .env file
4. Set up GitHub Actions secrets
5. Run first deployment

Useful Commands:
- Check SSL: certbot certificates
- Renew SSL: /usr/local/bin/renew-ssl.sh
- Daily backup: /usr/local/bin/daily-backup.sh
- Check firewall: ufw status
- Check fail2ban: fail2ban-client status

Generated on: $(date)
EOF

chown $DEPLOY_USER:$DEPLOY_USER /opt/novaya-lyada/SERVER_INFO.txt

echo -e "${GREEN}🎉 Server setup completed successfully!${NC}"
echo -e "${BLUE}📋 Setup information saved to /opt/novaya-lyada/SERVER_INFO.txt${NC}"
echo -e "${YELLOW}🔄 Please reboot the server to ensure all changes take effect${NC}"
echo -e "${YELLOW}📧 Next: Configure SSH keys for the $DEPLOY_USER user${NC}"

echo -e "${BLUE}Commands to add SSH key:${NC}"
echo -e "su - $DEPLOY_USER"
echo -e "mkdir -p ~/.ssh"
echo -e "echo 'YOUR_PUBLIC_KEY' >> ~/.ssh/authorized_keys"
echo -e "chmod 600 ~/.ssh/authorized_keys"
echo -e "chmod 700 ~/.ssh"
