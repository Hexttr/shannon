# Статус развертывания на сервере

## Выполнено

1. ✅ PHP 8.3 установлен
2. ✅ Composer установлен
3. ✅ Laravel Backend развернут в `/root/shannon/backend-laravel`
4. ✅ Frontend развернут в `/root/shannon/template`
5. ✅ База данных SQLite создана и миграции выполнены
6. ✅ Systemd service `shannon-laravel.service` создан и запущен
7. ✅ Nginx настроен для проксирования API запросов
8. ✅ Пользователь `admin` создан (логин: admin, пароль: admin)
9. ✅ Frontend собран и доступен

## Текущая проблема

API возвращает ошибку 500 при запросах. Требуется диагностика:

```bash
ssh root@72.56.79.153
cd /root/shannon/backend-laravel
tail -50 storage/logs/laravel.log
```

## Доступ к приложению

- **URL**: http://72.56.79.153
- **Логин**: admin
- **Пароль**: admin

## Команды для диагностики

```bash
# Проверка статуса backend
systemctl status shannon-laravel.service

# Просмотр логов
journalctl -u shannon-laravel.service -f

# Просмотр логов Laravel
tail -f /root/shannon/backend-laravel/storage/logs/laravel.log

# Тест API напрямую
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Проверка маршрутов
cd /root/shannon/backend-laravel
php artisan route:list
```

## Следующие шаги

1. Проверить логи Laravel для выявления конкретной ошибки
2. Убедиться, что все зависимости установлены: `composer install`
3. Проверить права доступа: `chmod -R 775 storage bootstrap/cache`
4. Очистить кэш: `php artisan optimize:clear`

