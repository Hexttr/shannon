# Руководство по миграции с Python/FastAPI на PHP/Laravel

## Обзор изменений

Backend приложение было переписано с Python/FastAPI на PHP/Laravel 11 с использованием принципов из книги "Laravel Beyond CRUD".

## Архитектурные изменения

### Структура проекта

**Было (Python/FastAPI):**
```
backend/app/
├── api/          # REST endpoints
├── core/         # Бизнес-логика
├── models/       # SQLAlchemy модели
└── schemas/      # Pydantic схемы
```

**Стало (PHP/Laravel):**
```
backend-laravel/app/
├── Domain/       # Доменная логика (Actions)
├── Data/         # DTO (spatie/laravel-data)
├── Http/         # Контроллеры и запросы
├── Models/       # Eloquent модели
└── Services/     # Внешние сервисы
```

## Основные компоненты

### 1. Data Transfer Objects (DTO)

Используется пакет `spatie/laravel-data` для передачи данных между слоями:

```php
// app/Data/Pentests/PentestData.php
class PentestData extends Data
{
    public function __construct(
        public string $id,
        public string $name,
        // ...
    ) {}
}
```

### 2. Domain Actions

Бизнес-логика вынесена в отдельные классы действий:

```php
// app/Domain/Pentests/Actions/CreatePentestAction.php
class CreatePentestAction
{
    public function execute(CreatePentestData $data): PentestData
    {
        // Логика создания пентеста
    }
}
```

### 3. Thin Controllers

Контроллеры только делегируют вызовы Actions:

```php
class PentestController extends Controller
{
    public function __construct(
        private CreatePentestAction $createAction
    ) {}

    public function store(Request $request)
    {
        $data = CreatePentestData::from($request->all());
        return $this->createAction->execute($data);
    }
}
```

## Миграция данных

### База данных

Структура БД осталась той же, но миграции переписаны на Laravel:

- `users` - пользователи
- `services` - сервисы для тестирования
- `pentests` - пентесты
- `vulnerabilities` - уязвимости
- `logs` - логи выполнения

### API Endpoints

Все endpoints остались теми же:

- `POST /api/auth/login` - вход
- `GET /api/auth/me` - текущий пользователь
- `GET /api/services` - список сервисов
- `POST /api/services` - создать сервис
- `DELETE /api/services/{id}` - удалить сервис
- `GET /api/pentests` - список пентестов
- `POST /api/pentests` - создать пентест
- `POST /api/pentests/{id}/start` - запустить пентест
- `POST /api/pentests/{id}/stop` - остановить пентест
- `DELETE /api/pentests/{id}` - удалить пентест
- `GET /api/pentests/{id}/vulnerabilities` - уязвимости пентеста
- `GET /api/pentests/{id}/logs` - логи пентеста

## Установка и запуск

### Требования

- PHP 8.2+
- Composer
- SQLite (или другая БД)

### Установка

```bash
cd backend-laravel
composer install
cp .env.example .env
php artisan key:generate
php artisan migrate
php artisan serve
```

### Конфигурация

Настройте переменные окружения в `.env`:

```env
CLAUDE_API_KEY=your_key
SSH_HOST=localhost
SSH_USERNAME=root
SSH_PASSWORD=your_password
```

## WebSocket

Для real-time обновлений используется Laravel Broadcasting с Pusher или Redis.

Настройте в `.env`:
```env
BROADCAST_DRIVER=pusher
PUSHER_APP_ID=...
PUSHER_APP_KEY=...
PUSHER_APP_SECRET=...
```

## Отличия от Python версии

1. **Асинхронность**: Вместо Python threading используется Laravel Queues
2. **SSH**: Используется `phpseclib3` вместо `paramiko`
3. **HTTP клиент**: Используется `guzzlehttp/guzzle` вместо `httpx`
4. **Валидация**: Используется Laravel Form Requests вместо Pydantic
5. **WebSocket**: Используется Laravel Broadcasting вместо Socket.IO

## Тестирование

```bash
php artisan test
```

## Дополнительные ресурсы

- [Laravel Beyond CRUD](https://laravel-beyond-crud.com/)
- [Spatie Laravel Data](https://github.com/spatie/laravel-data)
- [Laravel Documentation](https://laravel.com/docs)

