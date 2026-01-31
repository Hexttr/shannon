# Развертывание на сервере

## Быстрый развертывание

### 1. Развертывание Laravel Backend

```bash
python setup_laravel_on_server.py
```

Или вручную:

```bash
# Подключение к серверу
ssh root@72.56.79.153

# Клонирование репозитория (если еще не клонирован)
cd /root/shannon
git pull

# Переход в директорию Laravel backend
cd backend-laravel

# Установка зависимостей
composer install --no-dev --optimize-autoloader

# Настройка окружения
cp .env.example .env
php artisan key:generate

# Настройка базы данных в .env
# DB_CONNECTION=sqlite
# DB_DATABASE=/root/shannon/backend-laravel/database/database.sqlite

# Создание базы данных
touch database/database.sqlite

# Запуск миграций
php artisan migrate --force

# Настройка прав доступа
chmod -R 775 storage bootstrap/cache
chown -R www-data:www-data storage bootstrap/cache

# Оптимизация
php artisan config:cache
php artisan route:cache

# Создание systemd service
cat > /etc/systemd/system/shannon-laravel.service << 'EOF'
[Unit]
Description=Shannon Laravel Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/shannon/backend-laravel
ExecStart=/usr/bin/php /root/shannon/backend-laravel/artisan serve --host=0.0.0.0 --port=8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Запуск сервиса
systemctl daemon-reload
systemctl enable shannon-laravel.service
systemctl start shannon-laravel.service

# Проверка статуса
systemctl status shannon-laravel.service
```

### 2. Создание пользователя

```bash
ssh root@72.56.79.153
cd /root/shannon/backend-laravel
php artisan tinker
```

```php
\App\Models\User::create([
    'id' => \Illuminate\Support\Str::uuid(),
    'username' => 'admin',
    'email' => 'admin@shannon.local',
    'password' => \Illuminate\Support\Facades\Hash::make('your_secure_password'),
]);
```

### 3. Настройка Frontend

```bash
python setup_frontend_on_server.py
```

Или вручную:

```bash
ssh root@72.56.79.153
cd /root/shannon/template

# Создание .env
cat > .env << 'EOF'
VITE_API_URL=https://72.56.79.153/api
EOF

# Установка зависимостей
npm install

# Сборка
npm run build
```

### 4. Настройка Nginx

```bash
ssh root@72.56.79.153

# Создание конфигурации
cat > /etc/nginx/sites-available/shannon << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name 72.56.79.153;

    root /root/shannon/template/dist;
    index index.html;

    # Frontend (SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API проксирование к Laravel backend
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /up {
        proxy_pass http://127.0.0.1:8000/up;
        proxy_set_header Host $host;
    }
}
EOF

# Активация конфигурации
ln -sf /etc/nginx/sites-available/shannon /etc/nginx/sites-enabled/shannon

# Проверка и перезагрузка
nginx -t
systemctl reload nginx
```

### 5. Настройка SSL (опционально)

```bash
ssh root@72.56.79.153
certbot --nginx -d 72.56.79.153
```

## Проверка работоспособности

### Проверка Backend

```bash
# Проверка статуса сервиса
systemctl status shannon-laravel.service

# Проверка логов
journalctl -u shannon-laravel -f

# Проверка API
curl http://localhost:8000/api/auth/login
curl http://localhost:8000/up
```

### Проверка Frontend

```bash
# Проверка сборки
ls -la /root/shannon/template/dist

# Проверка Nginx
nginx -t
systemctl status nginx
```

### Проверка через браузер

1. Откройте: `http://72.56.79.153` или `https://72.56.79.153`
2. Войдите с учетными данными, созданными ранее
3. Проверьте работу всех функций

## Обновление приложения

```bash
ssh root@72.56.79.153
cd /root/shannon

# Обновление кода
git pull

# Обновление Backend
cd backend-laravel
composer install --no-dev --optimize-autoloader
php artisan migrate --force
php artisan config:cache
php artisan route:cache
systemctl restart shannon-laravel.service

# Обновление Frontend
cd ../template
npm install
npm run build
systemctl reload nginx
```

## Troubleshooting

### Backend не запускается

```bash
# Проверка логов
journalctl -u shannon-laravel -n 50

# Проверка прав доступа
ls -la /root/shannon/backend-laravel/storage
ls -la /root/shannon/backend-laravel/bootstrap/cache

# Ручной запуск для отладки
cd /root/shannon/backend-laravel
php artisan serve --host=0.0.0.0 --port=8000
```

### Frontend не загружается

```bash
# Проверка Nginx
nginx -t
systemctl status nginx

# Проверка файлов
ls -la /root/shannon/template/dist

# Проверка логов Nginx
tail -f /var/log/nginx/error.log
```

### Ошибки CORS

Проверьте `config/cors.php` в Laravel backend и убедитесь, что `FRONTEND_URL` настроен правильно.

