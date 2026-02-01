#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка через Nginx (как фронтенд)
"""

import sys
import os
import time

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def test_through_nginx(conn):
    """Тестирует через Nginx"""
    print("\n" + "="*60)
    print("🔍 Тестирование через Nginx...")
    print("="*60)
    
    # Тестируем через внешний IP (как фронтенд)
    endpoints = [
        ("https://72.56.79.153/api/pentests", "GET"),
        ("https://72.56.79.153/api/services", "GET"),
        ("https://72.56.79.153/up", "GET"),
    ]
    
    for endpoint, method in endpoints:
        print(f"\n{method} {endpoint}:")
        output, error, code = conn.execute(f"curl -s -k -w '\\nHTTP_CODE:%{{http_code}}' {endpoint} 2>&1")
        if output:
            if 'HTTP_CODE:500' in output:
                print("  ❌ 500 ошибка")
                # Показываем тело ответа
                body = output.split('HTTP_CODE:')[0]
                print(f"  Тело ответа: {body[:300]}")
            elif 'HTTP_CODE:401' in output:
                print("  ✅ 401 (ожидаемо без авторизации)")
            elif 'HTTP_CODE:200' in output:
                print("  ✅ 200 OK")
            else:
                print(f"  ⚠️  {output[-100:]}")

def check_nginx_logs(conn):
    """Проверяет логи Nginx"""
    print("\n" + "="*60)
    print("🔍 Проверка логов Nginx...")
    print("="*60)
    
    nginx_error_log = "/var/log/nginx/error.log"
    
    # Проверяем последние ошибки
    output, error, code = conn.execute(f"tail -n 50 {nginx_error_log} 2>&1 | grep -i error | tail -n 10")
    if output:
        print("Последние ошибки Nginx:")
        print(output)
    else:
        print("   Ошибок в логе Nginx не найдено")

def check_nginx_config(conn):
    """Проверяет конфигурацию Nginx"""
    print("\n" + "="*60)
    print("🔍 Проверка конфигурации Nginx...")
    print("="*60)
    
    # Проверяем синтаксис
    output, error, code = conn.execute("nginx -t 2>&1")
    if output:
        print(output)
        if 'syntax is ok' in output.lower():
            print("✅ Конфигурация Nginx правильная")
        else:
            print("❌ Ошибка в конфигурации Nginx")

def check_laravel_logs_after_nginx_request(conn):
    """Проверяет логи Laravel после запроса через Nginx"""
    print("\n" + "="*60)
    print("🔍 Проверка логов Laravel после запроса через Nginx...")
    print("="*60)
    
    log_file = "/root/shannon/backend-laravel/storage/logs/laravel.log"
    
    # Очищаем лог
    conn.execute(f"echo '' > {log_file}")
    
    # Делаем запрос через Nginx
    print("\n📡 Отправка запроса через Nginx...")
    conn.execute("curl -s -k https://72.56.79.153/api/pentests > /dev/null 2>&1")
    
    time.sleep(1)
    
    # Читаем ошибку
    output, error, code = conn.execute(f"cat {log_file} 2>&1")
    if output:
        print("Ошибка из лога Laravel:")
        print(output[:2000])
    else:
        print("   Лог пуст")

def main():
    """Главная функция"""
    print("="*60)
    print("🔍 Проверка через Nginx")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        check_nginx_config(conn)
        check_nginx_logs(conn)
        test_through_nginx(conn)
        check_laravel_logs_after_nginx_request(conn)
        
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


