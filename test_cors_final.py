#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная проверка CORS и логина
"""

import sys
import os
import json

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def test_cors_final():
    """Финальная проверка CORS"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("✅ ФИНАЛЬНАЯ ПРОВЕРКА CORS И ЛОГИНА")
        print("="*60)
        
        # 1. Тест OPTIONS (preflight)
        print("\n1. Тест OPTIONS запроса (preflight):")
        curl_cmd = 'curl -s -k -X OPTIONS https://72.56.79.153/api/auth/login -H "Origin: https://72.56.79.153" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: content-type" -i 2>&1'
        output, _, code = conn.execute(curl_cmd)
        print(output[:500])
        
        if 'access-control-allow-origin' in output.lower():
            print("✅ CORS заголовки присутствуют в OPTIONS ответе")
        else:
            print("❌ CORS заголовки отсутствуют")
        
        # 2. Тест POST запроса
        print("\n2. Тест POST запроса с Origin:")
        curl_cmd = 'curl -s -k -X POST https://72.56.79.153/api/auth/login -H "Origin: https://72.56.79.153" -H "Content-Type: application/json" -H "Accept: application/json" -d \'{"username":"admin","password":"admin"}\' -i 2>&1'
        output, _, code = conn.execute(curl_cmd)
        print(output[:600])
        
        if 'access-control-allow-origin' in output.lower():
            print("✅ CORS заголовки присутствуют в POST ответе")
        else:
            print("⚠️  CORS заголовки отсутствуют в POST ответе")
        
        if 'token' in output:
            print("✅ Логин работает!")
            try:
                # Извлекаем JSON из ответа
                json_start = output.find('{')
                if json_start > 0:
                    json_str = output[json_start:]
                    data = json.loads(json_str)
                    print(f"   Токен получен: {data.get('token', '')[:30]}...")
                    print(f"   Пользователь: {data.get('user', {}).get('username', 'N/A')}")
            except:
                pass
        
        # 3. Проверка конфигурации
        print("\n3. Проверка конфигурации:")
        output, _, _ = conn.execute('cat /root/shannon/backend-laravel/bootstrap/app.php | grep -A 5 "withMiddleware"')
        print(output)
        
        print("\n" + "="*60)
        print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
        print("="*60)
        print("\n💡 Если в браузере все еще network error:")
        print("   1. Откройте консоль браузера (F12)")
        print("   2. Проверьте вкладку Network")
        print("   3. Найдите запрос к /api/auth/login")
        print("   4. Проверьте заголовки запроса и ответа")
        print("   5. Убедитесь что Origin заголовок отправляется")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    test_cors_final()

