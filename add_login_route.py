#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Добавление маршрута login
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def add_login_route(conn):
    """Добавляет маршрут login"""
    print("\n" + "="*60)
    print("🔧 Добавление маршрута login...")
    print("="*60)
    
    file_path = "/root/shannon/backend-laravel/routes/web.php"
    
    # Читаем локальный файл
    with open("backend-laravel/routes/web.php", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Загружаем на сервер
    conn.execute(f"cat > {file_path} << 'EOFROUTES'\n{content}EOFROUTES")
    
    print("✅ Маршрут login добавлен")
    return True

def main():
    """Главная функция"""
    print("="*60)
    print("🔧 Добавление маршрута login")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        if add_login_route(conn):
            # Очищаем кэш маршрутов
            print("\n🧹 Очистка кэша маршрутов...")
            conn.execute("cd /root/shannon/backend-laravel && php artisan route:clear")
            
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
                    print("✅ API работает! (401 - ожидаемо без авторизации)")
                    print("\n✅ Проблема решена!")
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


