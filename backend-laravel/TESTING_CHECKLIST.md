# Чеклист для тестирования Laravel Backend

## ✅ Предварительная проверка

- [ ] PHP 8.2+ установлен
- [ ] Composer установлен
- [ ] Все зависимости установлены (`composer install`)
- [ ] `.env` файл создан и настроен
- [ ] `APP_KEY` сгенерирован (`php artisan key:generate`)
- [ ] База данных настроена
- [ ] Миграции выполнены (`php artisan migrate`)

## ✅ Базовое тестирование

### 1. Проверка здоровья приложения

```bash
curl http://localhost:8000/up
```

Ожидается: `{"status":"ok"}` или `200 OK`

### 2. Проверка API endpoints

```bash
# Проверка доступности API
curl http://localhost:8000/api/auth/login
```

Ожидается: ошибка валидации (нормально, так как нет данных)

### 3. Создание пользователя

```bash
php artisan tinker
```

```php
\App\Models\User::create([
    'id' => \Illuminate\Support\Str::uuid(),
    'username' => 'test',
    'email' => 'test@test.com',
    'password' => \Illuminate\Support\Facades\Hash::make('test123'),
]);
```

### 4. Тест аутентификации

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

Ожидается: JSON с `user` и `token`

### 5. Тест получения текущего пользователя

```bash
# Замените YOUR_TOKEN на токен из предыдущего запроса
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Ожидается: JSON с данными пользователя

## ✅ Тестирование функционала

### 1. Создание сервиса

```bash
curl -X POST http://localhost:8000/api/services \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"Test Service","url":"https://example.com"}'
```

### 2. Получение списка сервисов

```bash
curl http://localhost:8000/api/services \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Создание пентеста

```bash
curl -X POST http://localhost:8000/api/pentests \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"Test Pentest","config":{"targetUrl":"https://example.com"}}'
```

### 4. Запуск пентеста

```bash
# Замените PENTEST_ID на ID созданного пентеста
curl -X POST http://localhost:8000/api/pentests/PENTEST_ID/start \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Получение статуса пентеста

```bash
curl http://localhost:8000/api/pentests \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Получение уязвимостей

```bash
curl http://localhost:8000/api/pentests/PENTEST_ID/vulnerabilities \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. Получение логов

```bash
curl http://localhost:8000/api/pentests/PENTEST_ID/logs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## ✅ Тестирование ошибок

### 1. Неверные учетные данные

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"wrong","password":"wrong"}'
```

Ожидается: ошибка валидации

### 2. Неавторизованный доступ

```bash
curl http://localhost:8000/api/services
```

Ожидается: `401 Unauthorized`

### 3. Неверный формат данных

```bash
curl -X POST http://localhost:8000/api/services \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"Test"}'
```

Ожидается: ошибка валидации (отсутствует `url`)

## ✅ Проверка логов

```bash
tail -f storage/logs/laravel.log
```

## ✅ Проверка очередей (если используется)

```bash
# Запуск воркера
php artisan queue:work

# Проверка таблицы jobs
php artisan tinker
\DB::table('jobs')->get();
```

## Возможные проблемы

### Проблема: "Class not found"

**Решение:**
```bash
composer dump-autoload
php artisan optimize:clear
```

### Проблема: "SQLSTATE: no such table"

**Решение:**
```bash
php artisan migrate
```

### Проблема: "Storage directory not writable"

**Решение:**
```bash
chmod -R 775 storage bootstrap/cache
```

### Проблема: "CORS error" во frontend

**Решение:** Проверьте `config/cors.php` и настройте `FRONTEND_URL` в `.env`

## Готово к тестированию!

После выполнения всех проверок приложение готово к использованию.

