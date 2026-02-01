#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновление bootstrap/app.php на сервере
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def update_bootstrap_app(conn):
    """Обновляет bootstrap/app.php"""
    print("\n" + "="*60)
    print("🔧 Обновление bootstrap/app.php...")
    print("="*60)
    
    file_path = "/root/shannon/backend-laravel/bootstrap/app.php"
    
    # Читаем локальный файл
    with open("backend-laravel/bootstrap/app.php", "r", encoding="utf-8") as f:
        local_content = f.read()
    
    # Загружаем на сервер
    print("📤 Загрузка файла на сервер...")
    conn.execute(f"cat > {file_path} << 'EOFBOOTSTRAP'\n{local_content}EOFBOOTSTRAP")
    
    # Проверяем синтаксис
    output, error, code = conn.execute(f"php -l {file_path} 2>&1")
    if code == 0:
        print("✅ Файл обновлен и синтаксис правильный")
        return True
    else:
        print(f"❌ Синтаксическая ошибка: {error}")
        return False

def clear_caches_and_restart(conn):
    """Очищает кэши и перезапускает"""
    print("\n" + "="*60)
    print("🧹 Очистка кэшей и перезапуск...")
    print("="*60)
    
    conn.execute("cd /root/shannon/backend-laravel && php artisan optimize:clear 2>&1")
    conn.execute("systemctl restart shannon-laravel")
    
    import time
    time.sleep(3)
    
    # Тестируем
    print("\n🔍 Тестирование API...")
    output, error, code = conn.execute("curl -s -w '\\nHTTP_CODE:%{http_code}' http://localhost:8000/api/pentests 2>&1")
    if output:
        if 'HTTP_CODE:401' in output:
            print("✅ API работает! (401 - ожидаемо)")
            return True
        elif 'HTTP_CODE:500' in output:
            print("❌ Все еще 500 ошибка")
            return False
        else:
            print(f"⚠️  Статус: {output[-30:]}")
            return False

def main():
    """Главная функция"""
    print("="*60)
    print("🔧 Обновление bootstrap/app.php")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        if update_bootstrap_app(conn):
            clear_caches_and_restart(conn)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


