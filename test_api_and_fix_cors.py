#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование API и исправление CORS
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def test_api_and_fix():
    """Тестирует API и исправляет CORS"""
    print("Тестирование API и проверка CORS...")
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # Тест API напрямую
        print("\n[1] Тест API /auth/login:")
        output, error, code = conn.execute("curl -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' 2>&1")
        print(output[-500:] if output else "Нет ответа")
        
        # Проверка CORS конфигурации
        print("\n[2] Проверка CORS конфигурации:")
        output, error, code = conn.execute("cd /root/shannon/backend-laravel && grep -A 5 'FRONTEND_URL\|allowed_origins' config/cors.php")
        print(output)
        
        # Проверка .env для CORS
        print("\n[3] Проверка .env для CORS:")
        output, error, code = conn.execute("cd /root/shannon/backend-laravel && grep -E 'FRONTEND_URL|APP_URL' .env")
        print(output)
        
        # Тест с CORS заголовками
        print("\n[4] Тест API с CORS заголовками:")
        output, error, code = conn.execute("curl -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -H 'Origin: https://72.56.79.153' -H 'Access-Control-Request-Method: POST' -d '{\"username\":\"admin\",\"password\":\"admin\"}' -v 2>&1 | grep -E 'HTTP|Access-Control|Origin'")
        print(output)
        
        # Проверка что API доступен через Nginx
        print("\n[5] Тест API через Nginx:")
        output, error, code = conn.execute("curl -X POST https://72.56.79.153/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' 2>&1 | head -20")
        print(output)
        
        return True

if __name__ == "__main__":
    test_api_and_fix()

