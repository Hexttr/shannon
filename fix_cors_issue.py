#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление CORS проблемы
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_cors():
    """Проверяет CORS настройки"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 Проверка CORS...")
        print("="*60)
        
        # Тест OPTIONS запроса (preflight)
        print("\n1. Тест OPTIONS запроса (preflight):")
        curl_cmd = 'curl -s -X OPTIONS https://72.56.79.153/api/auth/login -H "Origin: https://72.56.79.153" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: content-type" -v 2>&1'
        output, error, code = conn.execute(curl_cmd)
        print(output)
        
        # Тест POST запроса с Origin
        print("\n2. Тест POST запроса с Origin заголовком:")
        curl_cmd = 'curl -s -X POST https://72.56.79.153/api/auth/login -H "Origin: https://72.56.79.153" -H "Content-Type: application/json" -H "Accept: application/json" -d \'{"username":"admin","password":"admin"}\' -v 2>&1 | head -30'
        output, error, code = conn.execute(curl_cmd)
        print(output)
        
        # Проверка конфигурации CORS в Laravel
        print("\n3. Проверка конфигурации CORS:")
        output, _, _ = conn.execute('cat /root/shannon/backend-laravel/config/cors.php')
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
    check_cors()

