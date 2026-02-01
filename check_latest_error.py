#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка последней ошибки в логах Laravel
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def get_latest_error(conn):
    """Получает последнюю ошибку"""
    print("\n" + "="*60)
    print("🔍 Последняя ошибка из лога...")
    print("="*60)
    
    log_file = "/root/shannon/backend-laravel/storage/logs/laravel.log"
    
    # Получаем последние 300 строк
    output, error, code = conn.execute(f"tail -n 300 {log_file} 2>&1 | grep -A 50 'ERROR\\|Exception\\|Fatal' | tail -n 100")
    
    if output:
        print(output)
    else:
        # Если не нашли через grep, показываем последние строки
        output, error, code = conn.execute(f"tail -n 50 {log_file} 2>&1")
        if output:
            print("Последние строки лога:")
            print(output)

def check_new_files_exist(conn):
    """Проверяет существование новых файлов"""
    print("\n" + "="*60)
    print("🔍 Проверка новых файлов...")
    print("="*60)
    
    files = [
        "backend-laravel/app/Services/Contracts/AiAnalysisServiceInterface.php",
        "backend-laravel/app/Services/OllamaApiService.php",
        "backend-laravel/app/Services/AiServiceFactory.php",
    ]
    
    for file_path in files:
        full_path = f"/root/shannon/{file_path}"
        output, error, code = conn.execute(f"test -f {full_path} && echo 'exists' || echo 'not-found'")
        if 'exists' in output:
            # Проверяем синтаксис
            output2, error2, code2 = conn.execute(f"php -l {full_path} 2>&1")
            if code2 == 0:
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} - синтаксическая ошибка:")
                print(f"   {error2}")
        else:
            print(f"❌ {file_path} - файл не найден")

def check_autoload(conn):
    """Проверяет autoload"""
    print("\n" + "="*60)
    print("🔍 Проверка Composer autoload...")
    print("="*60)
    
    output, error, code = conn.execute("cd /root/shannon/backend-laravel && composer dump-autoload 2>&1")
    if code == 0:
        print("✅ Autoload обновлен")
    else:
        print(f"⚠️  Ошибка: {error}")
        if output:
            print(f"   {output[:500]}")

def test_api_endpoint(conn):
    """Тестирует API endpoint"""
    print("\n" + "="*60)
    print("🔍 Тестирование API endpoint...")
    print("="*60)
    
    # Пробуем получить список пентестов (без авторизации должно быть 401, не 500)
    output, error, code = conn.execute("curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/pentests 2>&1")
    if output:
        status_code = output.strip()
        print(f"HTTP статус код: {status_code}")
        if status_code == '500':
            print("❌ 500 ошибка подтверждена")
        elif status_code == '401':
            print("✅ API работает (401 - ожидаемо без авторизации)")
        else:
            print(f"⚠️  Неожиданный статус: {status_code}")

def main():
    """Главная функция"""
    print("="*60)
    print("🔍 Диагностика 500 ошибки")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        get_latest_error(conn)
        check_new_files_exist(conn)
        check_autoload(conn)
        test_api_endpoint(conn)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


