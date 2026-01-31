# Установка и настройка Shannon Backend (Laravel)

## Требования

- PHP 8.2 или выше
- Composer 2.x
- SQLite 3.x (или MySQL/PostgreSQL)
- Расширения PHP:
  - OpenSSL
  - PDO
  - Mbstring
  - Tokenizer
  - XML
  - Ctype
  - JSON
  - BCMath
  - Fileinfo

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/Hexttr/shannon.git
cd shannon/backend-laravel
```

### 2. Установка зависимостей

```bash
composer install
```

### 3. Настройка окружения

```bash
cp .env.example .env
php artisan key:generate
```

### 4. Настройка базы данных

#### SQLite (по умолчанию)

```bash
touch database/database.sqlite
```

В `.env`:
```env
DB_CONNECTION=sqlite
DB_DATABASE=/absolute/path/to/database.sqlite
```

#### MySQL/PostgreSQL

В `.env`:
```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=shannon
DB_USERNAME=root
DB_PASSWORD=
```

### 5. Запуск миграций

```bash
php artisan migrate
```

### 6. Создание пользователя (опционально)

```bash
php artisan tinker
```

```php
$user = \App\Models\User::create([
    'id' => \Illuminate\Support\Str::uuid(),
    'username' => 'admin',
    'email' => 'admin@example.com',
    'password' => \Illuminate\Support\Facades\Hash::make('password'),
]);
```

### 7. Настройка внешних сервисов

#### Claude API

В `.env`:
```env
CLAUDE_API_KEY=your_claude_api_key
```

#### SSH (для удаленного выполнения команд)

В `.env`:
```env
SSH_HOST=localhost
SSH_USERNAME=root
SSH_PASSWORD=your_password
```

Если команды выполняются локально, оставьте значения по умолчанию.

### 8. Настройка WebSocket (опционально)

#### Pusher

В `.env`:
```env
BROADCAST_DRIVER=pusher
PUSHER_APP_ID=your_app_id
PUSHER_APP_KEY=your_app_key
PUSHER_APP_SECRET=your_app_secret
PUSHER_APP_CLUSTER=mt1
```

#### Redis (альтернатива Pusher)

В `.env`:
```env
BROADCAST_DRIVER=redis
REDIS_HOST=127.0.0.1
REDIS_PASSWORD=null
REDIS_PORT=6379
```

### 9. Запуск сервера

#### Development

```bash
php artisan serve
```

Сервер будет доступен по адресу `http://localhost:8000`

#### Production

Используйте веб-сервер (Nginx/Apache) с PHP-FPM.

Пример конфигурации Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/backend-laravel/public;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";

    index index.php;

    charset utf-8;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    error_page 404 /index.php;

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
```

## Настройка очередей

### Использование очередей для пентестов

В `.env`:
```env
QUEUE_CONNECTION=database
```

Создание таблиц для очередей:
```bash
php artisan queue:table
php artisan migrate
```

Запуск воркера очередей:
```bash
php artisan queue:work
```

### Использование Redis для очередей

В `.env`:
```env
QUEUE_CONNECTION=redis
```

## Установка инструментов пентестинга

На сервере должны быть установлены:

```bash
# Nmap
sudo apt-get install nmap

# Nikto
sudo apt-get install nikto

# Nuclei
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Dirb
sudo apt-get install dirb

# SQLMap
git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap-dev
```

## Проверка установки

### 1. Проверка версии PHP

```bash
php -v
# Должна быть версия 8.2 или выше
```

### 2. Проверка зависимостей

```bash
composer check-platform-reqs
```

### 3. Проверка конфигурации

```bash
php artisan config:cache
php artisan config:clear
```

### 4. Тестирование API

```bash
# Проверка доступности API
curl http://localhost:8000/api/auth/login
```

## Разрешения файлов

Убедитесь, что Laravel может писать в следующие директории:

```bash
chmod -R 775 storage bootstrap/cache
chown -R www-data:www-data storage bootstrap/cache
```

## Troubleshooting

### Ошибка "Class not found"

```bash
composer dump-autoload
php artisan optimize:clear
```

### Ошибка подключения к БД

Проверьте настройки в `.env` и убедитесь, что БД существует.

### Ошибка выполнения SSH команд

Проверьте настройки SSH в `.env` и доступность сервера.

### Ошибка Claude API

Проверьте правильность API ключа в `.env`.

## Дополнительные команды

### Очистка кэша

```bash
php artisan cache:clear
php artisan config:clear
php artisan route:clear
php artisan view:clear
```

### Оптимизация

```bash
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

### Генерация документации API

```bash
composer require darkaonline/l5-swagger
php artisan l5-swagger:generate
```

## Поддержка

При возникновении проблем создайте issue в репозитории GitHub.

