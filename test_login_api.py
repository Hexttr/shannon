#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование API логина
"""

import json
import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def test_login():
    """Тестирует API логина"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        # Тест 1: Проверка маршрутов
        print("="*60)
        print("1. Проверка маршрутов API...")
        print("="*60)
        output, _, _ = conn.execute('cd /root/shannon/backend-laravel && php artisan route:list | grep auth')
        print(output)
        
        # Тест 2: Проверка пользователей в БД
        print("\n" + "="*60)
        print("2. Проверка пользователей в базе данных...")
        print("="*60)
        output, _, _ = conn.execute('cd /root/shannon/backend-laravel && php artisan tinker --execute="echo User::all()->toJson();" 2>&1 | tail -20')
        print(output)
        
        # Тест 3: Тест API логина через curl
        print("\n" + "="*60)
        print("3. Тест API логина...")
        print("="*60)
        curl_cmd = """curl -s -X POST http://localhost:8000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -H "Accept: application/json" \\
  -d '{"username":"admin","password":"admin"}'"""
        
        output, error, code = conn.execute(curl_cmd)
        print(f"Exit code: {code}")
        print(f"Output: {output}")
        if error:
            print(f"Error: {error}")
        
        # Тест 4: Проверка логов Laravel
        print("\n" + "="*60)
        print("4. Последние записи в логах Laravel...")
        print("="*60)
        output, _, _ = conn.execute('tail -50 /root/shannon/backend-laravel/storage/logs/laravel.log')
        if output.strip():
            print(output)
        else:
            print("Логи пусты")
        
        # Тест 5: Проверка статуса сервиса
        print("\n" + "="*60)
        print("5. Статус Laravel сервиса...")
        print("="*60)
        output, _, _ = conn.execute('systemctl status shannon-laravel.service --no-pager | head -15')
        print(output)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    test_login()

