#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная проверка логина
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def final_check():
    """Финальная проверка логина"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("✅ ФИНАЛЬНАЯ ПРОВЕРКА ЛОГИНА")
        print("="*60)
        
        # 1. Проверка пользователя в БД
        print("\n1. Проверка пользователя в базе данных:")
        output, _, _ = conn.execute('cd /root/shannon/backend-laravel && php artisan tinker --execute="echo App\\\\Models\\\\User::where(\'username\', \'admin\')->first()->username ?? \'not found\';" 2>&1')
        print(f"   Пользователь: {output.strip()}")
        
        # 2. Тест логина через localhost
        print("\n2. Тест логина через localhost (8000):")
        curl_cmd = 'curl -s -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -H "Accept: application/json" -d \'{"username":"admin","password":"admin"}\''
        output, _, _ = conn.execute(curl_cmd)
        if 'token' in output:
            print("   ✅ Логин работает через localhost")
        else:
            print(f"   ❌ Логин не работает: {output[:100]}")
        
        # 3. Тест логина через HTTPS
        print("\n3. Тест логина через HTTPS (72.56.79.153):")
        curl_cmd = 'curl -s -k -X POST https://72.56.79.153/api/auth/login -H "Content-Type: application/json" -H "Accept: application/json" -d \'{"username":"admin","password":"admin"}\''
        output, _, _ = conn.execute(curl_cmd)
        if 'token' in output:
            print("   ✅ Логин работает через HTTPS")
            # Извлекаем токен для проверки
            import json
            try:
                data = json.loads(output)
                token = data.get('token', '')
                user = data.get('user', {})
                print(f"   Токен получен: {token[:30]}...")
                print(f"   Пользователь: {user.get('username', 'N/A')}")
            except:
                pass
        else:
            print(f"   ❌ Логин не работает: {output[:200]}")
        
        # 4. Проверка frontend
        print("\n4. Проверка frontend:")
        output, _, _ = conn.execute('test -f /root/shannon/template/dist/index.html && echo "exists" || echo "not-found"')
        if 'exists' in output:
            print("   ✅ Frontend собран и доступен")
        else:
            print("   ⚠️  Frontend не найден")
        
        # 5. Проверка статуса сервисов
        print("\n5. Статус сервисов:")
        output, _, _ = conn.execute('systemctl is-active shannon-laravel.service nginx.service')
        print(f"   {output}")
        
        print("\n" + "="*60)
        print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
        print("="*60)
        print("\n💡 Учетные данные для входа:")
        print("   URL: https://72.56.79.153")
        print("   Username: admin")
        print("   Password: admin")
        print("\n✅ Логин должен работать в браузере!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    final_check()

