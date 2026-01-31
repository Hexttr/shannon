# Развертывание Laravel Backend

## Быстрый старт

### 1. Установка зависимостей

```bash
cd backend-laravel
composer install
```

### 2. Настройка окружения

```bash
cp .env.example .env
php artisan key:generate
```

### 3. Настройка базы данных

Для SQLite:
```bash
touch database/database.sqlite
```

В `.env`:
```env
DB_CONNECTION=sqlite
DB_DATABASE=/absolute/path/to/database.sqlite
```

### 4. Запуск миграций

```bash
php artisan migrate
```

### 5. Создание пользователя

```bash
php artisan tinker
```

```php
\App\Models\User::create([
    'id' => \Illuminate\Support\Str::uuid(),
    'username' => 'admin',
    'email' => 'admin@example.com',
    'password' => \Illuminate\Support\Facades\Hash::make('password'),
]);
```

### 6. Настройка внешних сервисов

В `.env`:
```env
CLAUDE_API_KEY=your_key
SSH_HOST=localhost
SSH_USERNAME=root
SSH_PASSWORD=your_password
```

### 7. Запуск сервера

```bash
php artisan serve
```

API будет доступен по адресу: `http://localhost:8000/api`

## Production развертывание

### Требования

- PHP 8.2+
- Composer
- SQLite/MySQL/PostgreSQL
- Nginx/Apache

### Шаги

1. Установите зависимости: `composer install --optimize-autoloader --no-dev`
2. Настройте `.env` файл
3. Запустите миграции: `php artisan migrate --force`
4. Оптимизируйте: `php artisan config:cache && php artisan route:cache`
5. Настройте веб-сервер (см. INSTALLATION.md)

### Очереди

Для асинхронного выполнения пентестов:

```bash
php artisan queue:work
```

Или используйте supervisor для автоматического перезапуска.

## Проверка работоспособности

```bash
# Проверка API
curl http://localhost:8000/api/auth/login

# Проверка здоровья
curl http://localhost:8000/up
```

