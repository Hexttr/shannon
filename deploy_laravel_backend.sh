#!/bin/bash

# Скрипт развертывания Laravel Backend на сервере
# Использование: ./deploy_laravel_backend.sh

set -e

SSH_HOST="72.56.79.153"
SSH_USER="root"
SSH_PASSWORD="m8J@2_6whwza6U"
BACKEND_DIR="/root/shannon/backend-laravel"

echo "=========================================="
echo "Развертывание Laravel Backend на сервере"
echo "=========================================="

# Функция для выполнения команд на сервере
ssh_exec() {
    sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no "$SSH_USER@$SSH_HOST" "$@"
}

# Функция для копирования файлов на сервер
scp_copy() {
    sshpass -p "$SSH_PASSWORD" scp -o StrictHostKeyChecking=no -r "$1" "$SSH_USER@$SSH_HOST:$2"
}

echo "1. Создание директории на сервере..."
ssh_exec "mkdir -p $BACKEND_DIR"

echo "2. Копирование файлов Laravel backend..."
scp_copy "backend-laravel/*" "$BACKEND_DIR/"

echo "3. Установка зависимостей Composer..."
ssh_exec "cd $BACKEND_DIR && composer install --no-dev --optimize-autoloader"

echo "4. Настройка окружения..."
ssh_exec "cd $BACKEND_DIR && [ ! -f .env ] && cp .env.example .env || true"

echo "5. Генерация APP_KEY..."
ssh_exec "cd $BACKEND_DIR && php artisan key:generate --force"

echo "6. Настройка прав доступа..."
ssh_exec "cd $BACKEND_DIR && chmod -R 775 storage bootstrap/cache"
ssh_exec "cd $BACKEND_DIR && chown -R www-data:www-data storage bootstrap/cache"

echo "7. Запуск миграций..."
ssh_exec "cd $BACKEND_DIR && php artisan migrate --force"

echo "8. Оптимизация..."
ssh_exec "cd $BACKEND_DIR && php artisan config:cache"
ssh_exec "cd $BACKEND_DIR && php artisan route:cache"

echo "=========================================="
echo "Развертывание завершено!"
echo "=========================================="
echo ""
echo "Следующие шаги:"
echo "1. Настройте .env файл на сервере: $BACKEND_DIR/.env"
echo "2. Создайте пользователя: php artisan tinker"
echo "3. Настройте systemd service для автозапуска"
echo "4. Настройте Nginx для проксирования запросов"

