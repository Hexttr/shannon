# Быстрый старт Laravel Backend

## Шаг 1: Установка зависимостей

```bash
cd backend-laravel
composer install
```

## Шаг 2: Настройка окружения

```bash
cp .env.example .env
php artisan key:generate
```

## Шаг 3: Настройка базы данных

### Вариант A: SQLite (быстрый старт)

```bash
touch database/database.sqlite
```

В `.env`:
```env
DB_CONNECTION=sqlite
DB_DATABASE=/absolute/path/to/backend-laravel/database/database.sqlite
```

### Вариант B: MySQL/PostgreSQL

В `.env` укажите параметры подключения к БД.

## Шаг 4: Запуск миграций

```bash
php artisan migrate
```

## Шаг 5: Создание пользователя

### Вариант A: Через Seeder

В `database/seeders/DatabaseSeeder.php` раскомментируйте:
```php
$this->call([
    UserSeeder::class,
]);
```

Затем:
```bash
php artisan db:seed
```

### Вариант B: Через Tinker

```bash
php artisan tinker
```

```php
\App\Models\User::create([
    'id' => \Illuminate\Support\Str::uuid(),
    'username' => 'admin',
    'email' => 'admin@shannon.local',
    'password' => \Illuminate\Support\Facades\Hash::make('admin'),
]);
```

## Шаг 6: Настройка внешних сервисов (опционально)

В `.env`:
```env
# Claude API для анализа результатов
CLAUDE_API_KEY=your_claude_api_key

# SSH для удаленного выполнения команд (если нужно)
SSH_HOST=localhost
SSH_USERNAME=root
SSH_PASSWORD=your_password
```

Если команды выполняются локально, оставьте значения по умолчанию.

## Шаг 7: Запуск сервера

```bash
php artisan serve
```

API будет доступен по адресу: `http://localhost:8000/api`

## Шаг 8: Настройка очередей (для асинхронного выполнения пентестов)

В `.env`:
```env
QUEUE_CONNECTION=database
```

Создание таблиц для очередей (если еще не созданы):
```bash
php artisan migrate
```

Запуск воркера:
```bash
php artisan queue:work
```

## Проверка работоспособности

### Тест API

```bash
# Проверка доступности
curl http://localhost:8000/api/auth/login

# Проверка здоровья
curl http://localhost:8000/up
```

### Тест аутентификации

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

## Структура API

- `POST /api/auth/login` - Вход
- `GET /api/auth/me` - Текущий пользователь (требует токен)
- `GET /api/services` - Список сервисов
- `POST /api/services` - Создать сервис
- `DELETE /api/services/{id}` - Удалить сервис
- `GET /api/pentests` - Список пентестов
- `POST /api/pentests` - Создать пентест
- `POST /api/pentests/{id}/start` - Запустить пентест
- `POST /api/pentests/{id}/stop` - Остановить пентест
- `DELETE /api/pentests/{id}` - Удалить пентест
- `GET /api/pentests/{id}/vulnerabilities` - Уязвимости пентеста
- `GET /api/pentests/{id}/logs` - Логи пентеста

## Troubleshooting

### Ошибка "Class not found"

```bash
composer dump-autoload
php artisan optimize:clear
```

### Ошибка подключения к БД

Проверьте настройки в `.env` и убедитесь, что БД существует.

### Ошибка "Storage directory not writable"

```bash
chmod -R 775 storage bootstrap/cache
```

### Ошибка выполнения SSH команд

Проверьте настройки SSH в `.env` или используйте локальное выполнение команд.

## Production развертывание

См. `DEPLOYMENT.md` для детальных инструкций по production развертыванию.

