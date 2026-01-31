# Shannon Backend - Laravel

Backend API для платформы автоматизированного пентестинга Shannon.

## Архитектура

Проект следует принципам из книги [Laravel Beyond CRUD](https://laravel-beyond-crud.com/):

- **Domain Actions** - бизнес-логика в отдельных классах действий
- **Data Transfer Objects** - использование `spatie/laravel-data` для передачи данных между слоями
- **Query Objects** - сложные запросы вынесены в отдельные классы
- **Thin Controllers** - контроллеры только делегируют вызовы Actions
- **Domain Models** - модели содержат только бизнес-логику, связанную с сущностью

## Структура проекта

```
app/
├── Domain/                    # Доменные модели и логика
│   ├── Auth/
│   │   ├── Actions/          # Действия аутентификации
│   │   └── Models/           # Доменные модели
│   ├── Services/
│   │   ├── Actions/
│   │   └── Models/
│   ├── Pentests/
│   │   ├── Actions/
│   │   ├── Models/
│   │   └── Engine/           # Pentest Engine
│   ├── Vulnerabilities/
│   │   ├── Actions/
│   │   └── Models/
│   └── Logs/
│       ├── Actions/
│       └── Models/
├── Http/
│   ├── Controllers/          # Тонкие контроллеры
│   ├── Requests/             # Form Requests для валидации
│   └── Resources/            # API Resources
├── Data/                     # Data Transfer Objects (spatie/laravel-data)
│   ├── Auth/
│   ├── Services/
│   ├── Pentests/
│   ├── Vulnerabilities/
│   └── Logs/
├── Queries/                  # Query Objects для сложных запросов
├── Services/                 # Сервисы (SSH, Claude API, etc.)
└── Broadcasting/            # WebSocket события
```

## Установка

```bash
composer install
cp .env.example .env
php artisan key:generate
php artisan migrate
php artisan db:seed
```

## Запуск

```bash
php artisan serve
```

## Тестирование

```bash
php artisan test
```

