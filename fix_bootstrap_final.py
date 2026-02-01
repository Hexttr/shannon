#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальное исправление bootstrap/app.php
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def upload_bootstrap_app(conn):
    """Загружает исправленный bootstrap/app.php"""
    print("\n" + "="*60)
    print("🔧 Загрузка исправленного bootstrap/app.php...")
    print("="*60)
    
    file_path = "/root/shannon/backend-laravel/bootstrap/app.php"
    
    # Читаем локальный файл
    with open("backend-laravel/bootstrap/app.php", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Загружаем на сервер
    conn.execute(f"cat > {file_path} << 'EOFBOOTSTRAP'\n{content}EOFBOOTSTRAP")
    
    # Проверяем синтаксис
    output, error, code = conn.execute(f"php -l {file_path} 2>&1")
    if code == 0:
        print("✅ Файл загружен и синтаксис правильный")
        return True
    else:
        print(f"❌ Синтаксическая ошибка: {error}")
        return False

def main():
    """Главная функция"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        if upload_bootstrap_app(conn):
            # Очищаем кэш
            print("\n🧹 Очистка кэша...")
            conn.execute("cd /root/shannon/backend-laravel && php artisan optimize:clear")
            
            # Перезапускаем
            print("\n🔄 Перезапуск Laravel...")
            conn.execute("systemctl restart shannon-laravel")
            
            import time
            time.sleep(3)
            
            # Тестируем
            print("\n🔍 Тестирование API...")
            output, error, code = conn.execute("curl -s -w '\\nHTTP_CODE:%{http_code}' http://localhost:8000/api/pentests 2>&1")
            if output:
                if 'HTTP_CODE:401' in output:
                    print("✅ API работает! (401 - ожидаемо)")
                else:
                    print(f"⚠️  Статус: {output[-50:]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


