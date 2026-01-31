# Настройка Frontend для работы с Laravel Backend

## Быстрый старт

### 1. Установка зависимостей

```bash
cd template
npm install
```

### 2. Настройка переменных окружения

Создайте файл `.env`:

```bash
cp .env.example .env
```

В `.env` укажите URL вашего Laravel backend:

```env
VITE_API_URL=http://localhost:8000/api
```

Если backend работает на другом порту или домене, измените URL соответственно.

### 3. Запуск Laravel Backend

В отдельном терминале:

```bash
cd backend-laravel
php artisan serve
```

Backend будет доступен на `http://localhost:8000`

### 4. Запуск Frontend

```bash
cd template
npm run dev
```

Frontend будет доступен на `http://localhost:5173`

## Вход в систему

1. Откройте браузер: `http://localhost:5173`
2. Используйте учетные данные, созданные в Laravel backend:
   - Логин: `admin` (или тот, который вы создали)
   - Пароль: `admin` (или тот, который вы установили)

## Создание пользователя в Laravel Backend

Если еще не создали пользователя:

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

## Проверка работоспособности

### 1. Проверка подключения к API

Откройте консоль браузера (F12) и проверьте:
- Нет ли ошибок CORS
- Успешно ли проходят запросы к `/api/auth/login`

### 2. Проверка аутентификации

После входа проверьте:
- Токен сохраняется в `localStorage` (ключ `auth_token`)
- Пользователь сохраняется в `localStorage` (ключ `user`)
- Можно перейти на страницы `/home`, `/home/services`, `/home/pentests`

### 3. Проверка функционала

- **Сервисы**: Создание, просмотр, удаление сервисов
- **Пентесты**: Создание, запуск, просмотр пентестов
- **Уязвимости**: Просмотр найденных уязвимостей
- **Логи**: Просмотр логов выполнения пентестов

## Troubleshooting

### Ошибка CORS

Если видите ошибку CORS в консоли:

1. Проверьте `config/cors.php` в Laravel backend
2. Убедитесь, что `FRONTEND_URL` в `.env` Laravel указывает на `http://localhost:5173`
3. Очистите кэш: `php artisan config:clear`

### Ошибка 401 Unauthorized

- Проверьте, что токен сохраняется в `localStorage`
- Проверьте, что токен передается в заголовке `Authorization: Bearer TOKEN`
- Проверьте, что пользователь существует в базе данных

### Ошибка подключения к API

- Убедитесь, что Laravel backend запущен на `http://localhost:8000`
- Проверьте `VITE_API_URL` в `.env` frontend
- Проверьте, что прокси настроен в `vite.config.ts`

### Страница не загружается

- Проверьте консоль браузера на ошибки
- Проверьте Network tab в DevTools
- Убедитесь, что все зависимости установлены (`npm install`)

## Production сборка

```bash
npm run build
```

Собранные файлы будут в папке `dist/`. Настройте веб-сервер (Nginx/Apache) для раздачи этих файлов.

