#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка файла базы данных
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_database_file(conn):
    """Проверяет файл базы данных"""
    print("\n" + "="*60)
    print("🔍 Проверка файла базы данных...")
    print("="*60)
    
    db_path = "/root/shannon/backend-laravel/database/database.sqlite"
    
    # Проверяем существование
    output, error, code = conn.execute(f"test -f {db_path} && echo 'exists' || echo 'not-found'")
    if 'exists' in output:
        print(f"✅ Файл существует: {db_path}")
        
        # Проверяем права доступа
        output, error, code = conn.execute(f"ls -la {db_path}")
        if output:
            print(f"\n📋 Права доступа:")
            print(output)
        
        # Проверяем размер
        output, error, code = conn.execute(f"du -h {db_path}")
        if output:
            print(f"\n📊 Размер файла:")
            print(output)
        
        # Проверяем, может ли PHP прочитать файл
        output, error, code = conn.execute(f"php -r \"echo file_exists('{db_path}') ? 'readable' : 'not-readable';\"")
        if output:
            print(f"\n🔐 PHP может прочитать файл: {output.strip()}")
        
        return True
    else:
        print(f"❌ Файл НЕ существует: {db_path}")
        print("   Создаю файл заново...")
        
        # Создаем файл
        conn.execute(f"touch {db_path}")
        conn.execute(f"chmod 664 {db_path}")
        
        # Выполняем миграции
        output, error, code = conn.execute("cd /root/shannon/backend-laravel && php artisan migrate --force 2>&1")
        if code == 0:
            print("✅ База данных создана и миграции выполнены")
            return True
        else:
            print(f"❌ Ошибка миграций: {error}")
            return False

def check_env_config(conn):
    """Проверяет конфигурацию в .env"""
    print("\n" + "="*60)
    print("🔍 Проверка конфигурации .env...")
    print("="*60)
    
    env_file = "/root/shannon/backend-laravel/.env"
    
    output, error, code = conn.execute(f"grep -E 'DB_|DATABASE' {env_file} 2>&1")
    if output:
        print("Конфигурация базы данных:")
        print(output)
    else:
        print("⚠️  Не удалось прочитать конфигурацию")

def clear_cache(conn):
    """Очищает кэш Laravel"""
    print("\n" + "="*60)
    print("🧹 Очистка кэша Laravel...")
    print("="*60)
    
    commands = [
        "php artisan config:clear",
        "php artisan cache:clear",
        "php artisan route:clear",
        "php artisan view:clear",
    ]
    
    for cmd in commands:
        output, error, code = conn.execute(f"cd /root/shannon/backend-laravel && {cmd} 2>&1")
        if code == 0:
            print(f"✅ {cmd}")
        else:
            print(f"⚠️  {cmd}: {error}")

def main():
    """Главная функция"""
    print("="*60)
    print("🔍 Проверка базы данных")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        check_database_file(conn)
        check_env_config(conn)
        clear_cache(conn)
        
        print("\n" + "="*60)
        print("🔄 Перезапуск Laravel...")
        print("="*60)
        conn.execute("systemctl restart shannon-laravel")
        
        import time
        time.sleep(3)
        
        print("✅ Готово")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


