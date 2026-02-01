#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка текущей 500 ошибки
"""

import sys
import os
import time

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def get_current_error(conn):
    """Получает текущую ошибку"""
    print("\n" + "="*60)
    print("🔍 Получение текущей ошибки...")
    print("="*60)
    
    log_file = "/root/shannon/backend-laravel/storage/logs/laravel.log"
    
    # Очищаем лог для чистоты
    print("\n🧹 Очистка лога...")
    conn.execute(f"echo '' > {log_file}")
    
    # Делаем запрос к API
    print("\n📡 Отправка запроса к /api/pentests...")
    conn.execute("curl -s http://localhost:8000/api/pentests > /dev/null 2>&1")
    
    time.sleep(1)
    
    # Читаем ошибку
    print("\n📋 Ошибка из лога:")
    output, error, code = conn.execute(f"cat {log_file} 2>&1")
    if output:
        # Показываем полную ошибку
        print(output)
    else:
        print("   Лог пуст")

def test_different_endpoints(conn):
    """Тестирует разные endpoints"""
    print("\n" + "="*60)
    print("🔍 Тестирование разных endpoints...")
    print("="*60)
    
    endpoints = [
        ("/api/pentests", "GET"),
        ("/api/services", "GET"),
        ("/up", "GET"),
    ]
    
    for endpoint, method in endpoints:
        print(f"\n{method} {endpoint}:")
        output, error, code = conn.execute(f"curl -s -w '\\nHTTP_CODE:%{{http_code}}' http://localhost:8000{endpoint} 2>&1")
        if output:
            if 'HTTP_CODE:500' in output:
                print("  ❌ 500 ошибка")
            elif 'HTTP_CODE:401' in output:
                print("  ✅ 401 (ожидаемо без авторизации)")
            elif 'HTTP_CODE:200' in output:
                print("  ✅ 200 OK")
            else:
                print(f"  ⚠️  {output[-50:]}")

def check_laravel_status(conn):
    """Проверяет статус Laravel"""
    print("\n" + "="*60)
    print("🔍 Статус Laravel...")
    print("="*60)
    
    output, error, code = conn.execute("systemctl status shannon-laravel --no-pager | head -15")
    if output:
        print(output)

def main():
    """Главная функция"""
    print("="*60)
    print("🔍 Проверка текущей 500 ошибки")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        check_laravel_status(conn)
        get_current_error(conn)
        test_different_endpoints(conn)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


