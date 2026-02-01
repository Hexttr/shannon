# Быстрый старт - Frontend + Laravel Backend

## Шаг 1: Запуск Laravel Backend

Откройте первый терминал:

```bash
cd backend-laravel
composer install
cp .env.example .env
php artisan key:generate
php artisan migrate
php artisan serve
```

Backend будет доступен на `http://localhost:8000`

## Шаг 2: Создание пользователя (если еще не создан)

В новом терминале:

```bash
cd backend-laravel
php artisan tinker
```

```php
\App\Models\User::create([
    'id' => \Illuminate\Support\Str::uuid(),
    'username' => 'admin',
    'email' => 'admin@test.com',
    'password' => \Illuminate\Support\Facades\Hash::make('admin'),
]);
```

Выйдите из tinker: `exit`

## Шаг 3: Запуск Frontend

Откройте второй терминал:

```bash
cd template
npm install
npm run dev
```

Frontend будет доступен на `http://localhost:5173`

## Шаг 4: Вход в систему

1. Откройте браузер: `http://localhost:5173`
2. Введите учетные данные:
   - **Логин:** `admin`
   - **Пароль:** `admin`
3. Нажмите "Войти"

## Что проверить после входа:

✅ Переход на главную страницу (`/home`)  
✅ Просмотр списка сервисов (`/home/services`)  
✅ Создание нового сервиса  
✅ Просмотр списка пентестов (`/home/pentests`)  
✅ Создание и запуск пентеста  

## Troubleshooting

### Ошибка CORS

Если видите ошибку CORS в консоли браузера:

1. Проверьте, что Laravel backend запущен на `http://localhost:8000`
2. В `backend-laravel/.env` добавьте:
   ```env
   FRONTEND_URL=http://localhost:5173
   ```
3. Очистите кэш: `php artisan config:clear`

### Ошибка подключения к API

- Убедитесь, что backend запущен (`php artisan serve`)
- Проверьте консоль браузера (F12) на ошибки
- Проверьте Network tab - должны быть запросы к `http://localhost:8000/api/*`

### Страница не загружается

- Проверьте, что все зависимости установлены (`npm install`)
- Проверьте консоль браузера на ошибки JavaScript
- Убедитесь, что frontend запущен (`npm run dev`)

## Готово! 🎉

Теперь вы можете тестировать приложение!


