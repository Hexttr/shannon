#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка 500 ошибки на сервере
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_laravel_logs(conn):
    """Проверяет логи Laravel"""
    print("\n" + "="*60)
    print("🔍 Проверка логов Laravel...")
    print("="*60)
    
    log_file = "/root/shannon/backend-laravel/storage/logs/laravel.log"
    
    # Проверяем последние 50 строк лога
    print("\n📋 Последние ошибки из лога:")
    output, error, code = conn.execute(f"tail -n 50 {log_file} 2>&1")
    if output:
        # Показываем только ошибки и предупреждения
        lines = output.split('\n')
        error_lines = [line for line in lines if 'ERROR' in line or 'Exception' in line or 'Error' in line or 'Fatal' in line]
        if error_lines:
            print("\n".join(error_lines[-20:]))  # Последние 20 ошибок
        else:
            print("   Последние строки лога:")
            print("\n".join(lines[-10:]))
    else:
        print("   Лог пуст или недоступен")

def check_laravel_service(conn):
    """Проверяет статус Laravel сервиса"""
    print("\n" + "="*60)
    print("🔍 Проверка Laravel сервиса...")
    print("="*60)
    
    output, error, code = conn.execute("systemctl status shannon-laravel --no-pager | head -15")
    if output:
        print(output)
    
    # Проверяем, запущен ли PHP-FPM или Laravel
    output, error, code = conn.execute("ps aux | grep -E 'php.*artisan|php.*laravel' | grep -v grep")
    if output:
        print("\n✅ Laravel процессы запущены:")
        print(output)
    else:
        print("\n⚠️  Laravel процессы не найдены")

def check_syntax_errors(conn):
    """Проверяет синтаксические ошибки в PHP файлах"""
    print("\n" + "="*60)
    print("🔍 Проверка синтаксиса PHP файлов...")
    print("="*60)
    
    files_to_check = [
        "backend-laravel/app/Services/Contracts/AiAnalysisServiceInterface.php",
        "backend-laravel/app/Services/OllamaApiService.php",
        "backend-laravel/app/Services/AiServiceFactory.php",
        "backend-laravel/app/Services/ClaudeApiService.php",
        "backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php",
    ]
    
    for file_path in files_to_check:
        full_path = f"/root/shannon/{file_path}"
        output, error, code = conn.execute(f"php -l {full_path} 2>&1")
        if code == 0:
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}: {error}")

def check_composer_autoload(conn):
    """Проверяет autoload Composer"""
    print("\n" + "="*60)
    print("🔍 Проверка Composer autoload...")
    print("="*60)
    
    output, error, code = conn.execute("cd /root/shannon/backend-laravel && composer dump-autoload 2>&1")
    if code == 0:
        print("✅ Autoload обновлен")
    else:
        print(f"⚠️  Ошибка обновления autoload: {error}")

def check_api_endpoint(conn):
    """Проверяет доступность API"""
    print("\n" + "="*60)
    print("🔍 Проверка доступности API...")
    print("="*60)
    
    # Проверяем health check endpoint
    output, error, code = conn.execute("curl -s http://localhost:8000/up 2>&1")
    if output and 'ok' in output.lower():
        print("✅ API доступен")
    else:
        print(f"⚠️  API недоступен: {output}")

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
        # Проверка логов
        check_laravel_logs(conn)
        
        # Проверка сервиса
        check_laravel_service(conn)
        
        # Проверка синтаксиса
        check_syntax_errors(conn)
        
        # Проверка autoload
        check_composer_autoload(conn)
        
        # Проверка API
        check_api_endpoint(conn)
        
        print("\n" + "="*60)
        print("✅ Диагностика завершена")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()
