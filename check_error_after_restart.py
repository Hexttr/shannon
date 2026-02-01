#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка ошибок после перезапуска
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def get_recent_errors(conn):
    """Получает недавние ошибки"""
    print("\n" + "="*60)
    print("🔍 Последние ошибки (последние 2 минуты)...")
    print("="*60)
    
    log_file = "/root/shannon/backend-laravel/storage/logs/laravel.log"
    
    # Получаем ошибки за последние 2 минуты
    output, error, code = conn.execute(f"tail -n 500 {log_file} 2>&1 | grep -A 30 'ERROR\\|Exception\\|Fatal' | tail -n 150")
    
    if output:
        print(output)
    else:
        print("   Недавних ошибок не найдено")

def test_api_directly(conn):
    """Тестирует API напрямую"""
    print("\n" + "="*60)
    print("🔍 Тестирование API...")
    print("="*60)
    
    # Тестируем endpoint без авторизации (должен быть 401, не 500)
    output, error, code = conn.execute("curl -s -w '\\nHTTP_CODE:%{http_code}' http://localhost:8000/api/pentests 2>&1")
    if output:
        if 'HTTP_CODE:500' in output:
            print("❌ 500 ошибка все еще присутствует")
            # Показываем тело ответа
            body = output.split('HTTP_CODE:')[0]
            print(f"\nТело ответа:")
            print(body[:500])
        elif 'HTTP_CODE:401' in output:
            print("✅ API работает (401 - ожидаемо без авторизации)")
        else:
            print(f"⚠️  Неожиданный статус: {output[-20:]}")

def check_class_loading(conn):
    """Проверяет загрузку классов"""
    print("\n" + "="*60)
    print("🔍 Проверка загрузки классов...")
    print("="*60)
    
    classes_to_check = [
        "App\\Services\\Contracts\\AiAnalysisServiceInterface",
        "App\\Services\\OllamaApiService",
        "App\\Services\\AiServiceFactory",
    ]
    
    for class_name in classes_to_check:
        escaped_class = class_name.replace("\\", "\\\\")
        output, error, code = conn.execute(f"cd /root/shannon/backend-laravel && php artisan tinker --execute=\"echo class_exists('{class_name}') ? 'OK' : 'NOT_FOUND';\" 2>&1")
        if output:
            if 'OK' in output:
                print(f"✅ {class_name}")
            else:
                print(f"❌ {class_name} - класс не найден")
                print(f"   {output}")

def main():
    """Главная функция"""
    print("="*60)
    print("🔍 Проверка после перезапуска")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        get_recent_errors(conn)
        check_class_loading(conn)
        test_api_directly(conn)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


