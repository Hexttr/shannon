#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование с просмотром логов в реальном времени
"""

import sys
import os
import time

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def test_with_logs(conn):
    """Тестирует API и смотрит логи"""
    print("\n" + "="*60)
    print("🔍 Тестирование с просмотром логов...")
    print("="*60)
    
    log_file = "/root/shannon/backend-laravel/storage/logs/laravel.log"
    
    # Очищаем старые логи для чистоты
    print("\n🧹 Очистка старых логов...")
    conn.execute(f"echo '' > {log_file}")
    
    # Делаем запрос
    print("\n📡 Отправка запроса к API...")
    output, error, code = conn.execute("curl -s -w '\\nHTTP_CODE:%{http_code}' http://localhost:8000/api/pentests 2>&1")
    
    # Ждем немного для записи в лог
    time.sleep(1)
    
    # Читаем новые логи
    print("\n📋 Новые ошибки в логе:")
    output2, error2, code2 = conn.execute(f"cat {log_file} 2>&1 | grep -A 50 'ERROR\\|Exception\\|Fatal' | head -100")
    
    if output2:
        print(output2)
    else:
        print("   Ошибок не найдено в логе")
        # Показываем последние строки лога
        output3, error3, code3 = conn.execute(f"tail -n 20 {log_file}")
        if output3:
            print("\nПоследние строки лога:")
            print(output3)

def check_dependency_injection(conn):
    """Проверяет dependency injection"""
    print("\n" + "="*60)
    print("🔍 Проверка dependency injection...")
    print("="*60)
    
    # Проверяем, может ли Laravel создать экземпляр AiServiceFactory
    test_script = """
try {
    \$factory = app(App\\Services\\AiServiceFactory::class);
    echo 'OK';
} catch (Exception \$e) {
    echo 'ERROR: ' . \$e->getMessage();
}
"""
    
    output, error, code = conn.execute(f"cd /root/shannon/backend-laravel && php artisan tinker --execute=\"{test_script}\" 2>&1")
    if output:
        if 'OK' in output:
            print("✅ AiServiceFactory создается успешно")
        else:
            print(f"❌ Ошибка создания AiServiceFactory: {output}")
    
    # Проверяем PentestEngine
    test_script2 = """
try {
    \$engine = app(App\\Domain\\Pentests\\Engine\\PentestEngine::class);
    echo 'OK';
} catch (Exception \$e) {
    echo 'ERROR: ' . \$e->getMessage();
}
"""
    
    output2, error2, code2 = conn.execute(f"cd /root/shannon/backend-laravel && php artisan tinker --execute=\"{test_script2}\" 2>&1")
    if output2:
        if 'OK' in output2:
            print("✅ PentestEngine создается успешно")
        else:
            print(f"❌ Ошибка создания PentestEngine: {output2}")

def main():
    """Главная функция"""
    print("="*60)
    print("🔍 Тестирование с логами")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        check_dependency_injection(conn)
        test_with_logs(conn)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


