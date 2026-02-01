#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование логина через внешний IP
"""

import json
import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def test_external_login():
    """Тестирует логин через внешний IP"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🌐 Тестирование логина через внешний IP...")
        print("="*60)
        
        # Тест через внешний IP
        curl_cmd = 'curl -s -X POST http://72.56.79.153/api/auth/login -H "Content-Type: application/json" -H "Accept: application/json" -d \'{"username":"admin","password":"admin"}\''
        
        output, error, code = conn.execute(curl_cmd)
        print(f"\n1. Тест через внешний IP (72.56.79.153):")
        print(f"   Exit code: {code}")
        print(f"   Response: {output[:300] if output else 'No output'}...")
        
        if output and 'token' in output:
            print("   ✅ Логин работает через внешний IP")
        else:
            print("   ❌ Логин не работает через внешний IP")
            if output:
                print(f"   Полный ответ: {output}")
        
        # Проверка конфигурации Nginx
        print("\n2. Проверка конфигурации Nginx:")
        nginx_cmd = 'grep -A 10 "location /api" /etc/nginx/sites-enabled/* 2>/dev/null | head -15'
        output, _, _ = conn.execute(nginx_cmd)
        if output:
            print(output)
        else:
            print("   ⚠️  Конфигурация не найдена")
        
        # Проверка логов Nginx
        print("\n3. Последние ошибки Nginx:")
        nginx_log_cmd = "tail -20 /var/log/nginx/error.log 2>/dev/null | tail -5"
        output, _, _ = conn.execute(nginx_log_cmd)
        if output and output.strip():
            print(output)
        else:
            print("   Нет ошибок")
        
        # Проверка логов Laravel
        print("\n4. Последние записи в логах Laravel:")
        laravel_log_cmd = "tail -30 /root/shannon/backend-laravel/storage/logs/laravel.log"
        output, _, _ = conn.execute(laravel_log_cmd)
        if output and output.strip():
            print(output[-500:])  # Последние 500 символов
        else:
            print("   Логи пусты")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    test_external_login()
