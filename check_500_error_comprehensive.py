#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексная проверка 500 ошибки на сервере
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def check_server_status():
    """Проверяет статус сервера и логи"""
    print("=" * 60)
    print("Проверка статуса сервера и диагностика 500 ошибки")
    print("=" * 60)
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return
        
        # 1. Проверка статуса Laravel сервиса
        print("\n[1] Статус Laravel сервиса:")
        output, error, code = conn.execute("systemctl status shannon-laravel.service --no-pager | head -15")
        print(output)
        
        # 2. Последние ошибки из Laravel логов
        print("\n[2] Последние ошибки из Laravel логов:")
        output, error, code = conn.execute("tail -100 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -A 10 -B 5 'ERROR\\|Exception\\|500' | tail -50")
        print(output)
        
        # 3. Полный последний лог Laravel
        print("\n[3] Последние 50 строк Laravel лога:")
        output, error, code = conn.execute("tail -50 /root/shannon/backend-laravel/storage/logs/laravel.log")
        print(output)
        
        # 4. Проверка прав доступа
        print("\n[4] Проверка прав доступа:")
        output, error, code = conn.execute("ls -la /root/shannon/backend-laravel/storage/logs/ | head -5")
        print(output)
        output, error, code = conn.execute("ls -la /root/shannon/backend-laravel/bootstrap/cache/ | head -5")
        print(output)
        
        # 5. Проверка конфигурации Nginx
        print("\n[5] Конфигурация Nginx:")
        output, error, code = conn.execute("cat /etc/nginx/sites-available/shannon")
        print(output)
        
        # 6. Проверка ошибок Nginx
        print("\n[6] Последние ошибки Nginx:")
        output, error, code = conn.execute("tail -30 /var/log/nginx/error.log")
        print(output)
        
        # 7. Тест API напрямую
        print("\n[7] Тест API напрямую:")
        output, error, code = conn.execute("curl -v http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' 2>&1")
        print(output)
        
        # 8. Проверка маршрутов Laravel
        print("\n[8] Проверка маршрутов Laravel:")
        output, error, code = conn.execute("cd /root/shannon/backend-laravel && php artisan route:list | head -20")
        print(output)
        
        # 9. Проверка .env файла (без секретов)
        print("\n[9] Проверка конфигурации .env (без секретов):")
        output, error, code = conn.execute("cd /root/shannon/backend-laravel && grep -E '^APP_|^DB_|^FRONTEND_|^SANCTUM_' .env | head -20")
        print(output)
        
        # 10. Проверка PHP ошибок
        print("\n[10] Проверка PHP логов:")
        output, error, code = conn.execute("tail -30 /var/log/php8.3-fpm.log 2>/dev/null || tail -30 /var/log/php-fpm.log 2>/dev/null || echo 'PHP лог не найден'")
        print(output)

if __name__ == "__main__":
    check_server_status()


