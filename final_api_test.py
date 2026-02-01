#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная проверка API
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def test_api_endpoints(conn):
    """Тестирует API endpoints"""
    print("\n" + "="*60)
    print("🔍 Тестирование API endpoints...")
    print("="*60)
    
    # Тест без авторизации (должен быть 401)
    print("\n1. Тест /api/pentests без авторизации:")
    output, error, code = conn.execute("curl -s -w '\\nHTTP_CODE:%{http_code}' http://localhost:8000/api/pentests 2>&1")
    if output:
        if 'HTTP_CODE:401' in output:
            print("✅ 401 Unauthorized (ожидаемо)")
        elif 'HTTP_CODE:500' in output:
            print("❌ 500 Internal Server Error")
            body = output.split('HTTP_CODE:')[0]
            print(f"   Тело ответа: {body[:300]}")
        else:
            print(f"⚠️  Неожиданный статус: {output[-30:]}")
    
    # Тест health check
    print("\n2. Тест /up:")
    output, error, code = conn.execute("curl -s http://localhost:8000/up 2>&1 | head -5")
    if output and ('ok' in output.lower() or 'up' in output.lower()):
        print("✅ Health check работает")
    else:
        print(f"⚠️  Health check: {output[:100]}")

def check_latest_logs(conn):
    """Проверяет последние логи"""
    print("\n" + "="*60)
    print("🔍 Последние логи (последние 30 строк)...")
    print("="*60)
    
    log_file = "/root/shannon/backend-laravel/storage/logs/laravel.log"
    output, error, code = conn.execute(f"tail -n 30 {log_file} 2>&1 | grep -E 'ERROR|Exception|Fatal|production' | tail -n 10")
    
    if output:
        print(output)
    else:
        print("   Ошибок не найдено")

def check_laravel_status(conn):
    """Проверяет статус Laravel"""
    print("\n" + "="*60)
    print("🔍 Статус Laravel...")
    print("="*60)
    
    output, error, code = conn.execute("systemctl status shannon-laravel --no-pager | head -12")
    if output:
        print(output)
        
        if 'active (running)' in output:
            print("✅ Laravel работает")

def main():
    """Главная функция"""
    print("="*60)
    print("🔍 Финальная проверка API")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        check_laravel_status(conn)
        check_latest_logs(conn)
        test_api_endpoints(conn)
        
        print("\n" + "="*60)
        print("✅ Проверка завершена")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


