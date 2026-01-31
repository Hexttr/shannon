#!/bin/bash

# Полное развертывание приложения на сервере
# Устанавливает зависимости и развертывает Laravel Backend + Frontend

set -e

SSH_HOST="72.56.79.153"
SSH_USER="root"
SSH_PASSWORD="m8J@2_6whwza6U"
BACKEND_DIR="/root/shannon/backend-laravel"
FRONTEND_DIR="/root/shannon/template"

echo "=========================================="
echo "ПОЛНОЕ РАЗВЕРТЫВАНИЕ НА СЕРВЕРЕ"
echo "=========================================="

# Функция для выполнения команд на сервере
ssh_exec() {
    sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no "$SSH_USER@$SSH_HOST" "$@"
}

echo "1. УСТАНОВКА PHP И ЗАВИСИМОСТЕЙ..."
ssh_exec "apt-get update && apt-get install -y php8.2 php8.2-cli php8.2-fpm php8.2-mbstring php8.2-xml php8.2-curl php8.2-sqlite3 php8.2-zip php8.2-gd php8.2-bcmath"

echo "2. УСТАНОВКА COMPOSER..."
ssh_exec "curl -sS https://getcomposer.org/installer | php && mv composer.phar /usr/local/bin/composer && chmod +x /usr/local/bin/composer"

echo "3. УСТАНОВКА NODE.JS И NPM..."
ssh_exec "curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs"

echo "4. КЛОНИРОВАНИЕ/ОБНОВЛЕНИЕ РЕПОЗИТОРИЯ..."
ssh_exec "cd /root/shannon && git pull || (git clone https://github.com/Hexttr/shannon.git /root/shannon)"

echo "5. РАЗВЕРТЫВАНИЕ LARAVEL BACKEND..."
ssh_exec "cd $BACKEND_DIR && composer install --no-dev --optimize-autoloader"
ssh_exec "cd $BACKEND_DIR && [ ! -f .env ] && cp .env.example .env || true"
ssh_exec "cd $BACKEND_DIR && php artisan key:generate --force"
ssh_exec "cd $BACKEND_DIR && touch database/database.sqlite"
ssh_exec "cd $BACKEND_DIR && php artisan migrate --force"
ssh_exec "cd $BACKEND_DIR && chmod -R 775 storage bootstrap/cache"
ssh_exec "cd $BACKEND_DIR && php artisan config:cache && php artisan route:cache"

echo "6. СОЗДАНИЕ SYSTEMD SERVICE..."
ssh_exec "cat > /etc/systemd/system/shannon-laravel.service << 'EOF'
[Unit]
Description=Shannon Laravel Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$BACKEND_DIR
ExecStart=/usr/bin/php $BACKEND_DIR/artisan serve --host=0.0.0.0 --port=8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

ssh_exec "systemctl daemon-reload && systemctl enable shannon-laravel.service && systemctl restart shannon-laravel.service"

echo "7. РАЗВЕРТЫВАНИЕ FRONTEND..."
ssh_exec "cd $FRONTEND_DIR && cat > .env << 'EOF'
VITE_API_URL=https://$SSH_HOST/api
EOF"
ssh_exec "cd $FRONTEND_DIR && npm install && npm run build"

echo "8. НАСТРОЙКА NGINX..."
ssh_exec "cat > /etc/nginx/sites-available/shannon << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name $SSH_HOST;

    root $FRONTEND_DIR/dist;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /up {
        proxy_pass http://127.0.0.1:8000/up;
        proxy_set_header Host \$host;
    }
}
EOF"

ssh_exec "ln -sf /etc/nginx/sites-available/shannon /etc/nginx/sites-enabled/shannon"
ssh_exec "rm -f /etc/nginx/sites-enabled/default"
ssh_exec "nginx -t && systemctl reload nginx"

echo "=========================================="
echo "РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=========================================="
echo ""
echo "Приложение доступно на: http://$SSH_HOST"
echo ""
echo "Создайте пользователя:"
echo "  ssh $SSH_USER@$SSH_HOST"
echo "  cd $BACKEND_DIR"
echo "  php artisan tinker"
echo "  \\App\\Models\\User::create(['id' => \\Illuminate\\Support\\Str::uuid(), 'username' => 'admin', 'email' => 'admin@test.com', 'password' => \\Illuminate\\Support\\Facades\\Hash::make('admin')]);"

