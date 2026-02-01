#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка конфигурации базы данных
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_database_config(conn):
    """Проверяет конфигурацию базы данных"""
    print("\n" + "="*60)
    print("🔍 Проверка конфигурации базы данных...")
    print("="*60)
    
    # Проверяем config/database.php
    config_file = "/root/shannon/backend-laravel/config/database.php"
    
    output, error, code = conn.execute(f"grep -A 10 'sqlite' {config_file} 2>&1")
    if output:
        print("Конфигурация SQLite:")
        print(output)
    
    # Проверяем через artisan tinker какой путь используется
    print("\n🔍 Проверка пути через Laravel...")
    output, error, code = conn.execute("cd /root/shannon/backend-laravel && php artisan tinker --execute=\"echo config('database.connections.sqlite.database');\" 2>&1")
    if output:
        print(f"Путь к базе данных в Laravel:")
        print(output)
        
        # Проверяем, существует ли файл по этому пути
        db_path = output.strip().strip('"').strip("'")
        if db_path:
            output2, error2, code2 = conn.execute(f"test -f {db_path} && echo 'exists' || echo 'not-found'")
            if 'exists' in output2:
                print(f"✅ Файл по пути Laravel существует")
            else:
                print(f"❌ Файл по пути Laravel НЕ существует: {db_path}")
                print("   Создаю симлинк или копирую файл...")
                
                # Пытаемся создать симлинк
                actual_db = "/root/shannon/backend-laravel/database/database.sqlite"
                if db_path != actual_db:
                    conn.execute(f"mkdir -p $(dirname {db_path})")
                    conn.execute(f"ln -sf {actual_db} {db_path} 2>&1 || cp {actual_db} {db_path}")

def test_database_connection(conn):
    """Тестирует подключение к базе данных"""
    print("\n" + "="*60)
    print("🔍 Тестирование подключения к базе данных...")
    print("="*60)
    
    output, error, code = conn.execute("cd /root/shannon/backend-laravel && php artisan tinker --execute=\"try { DB::connection()->getPdo(); echo 'OK'; } catch (Exception \\$e) { echo 'ERROR: ' . \\$e->getMessage(); }\" 2>&1")
    if output:
        print(output)
        if 'OK' in output:
            print("✅ Подключение к базе данных работает")
            return True
        else:
            print("❌ Ошибка подключения к базе данных")
            return False
    else:
        print("⚠️  Не удалось проверить подключение")
        return False

def fix_database_path(conn):
    """Исправляет путь к базе данных"""
    print("\n" + "="*60)
    print("🔧 Исправление пути к базе данных...")
    print("="*60)
    
    # Проверяем .env
    env_file = "/root/shannon/backend-laravel/.env"
    
    # Убеждаемся что DB_DATABASE не установлен (для SQLite это не нужно)
    output, error, code = conn.execute(f"grep '^DB_DATABASE' {env_file} 2>&1")
    if output:
        print("⚠️  DB_DATABASE установлен в .env, удаляю...")
        conn.execute(f"sed -i '/^DB_DATABASE/d' {env_file}")
    
    # Проверяем config/database.php - путь должен быть абсолютным
    config_file = "/root/shannon/backend-laravel/config/database.php"
    
    # Проверяем текущий путь
    output, error, code = conn.execute(f"grep -A 2 \"'database' =>\" {config_file} | grep sqlite -A 2")
    if output:
        print("Текущая конфигурация:")
        print(output)
        
        # Если путь относительный, делаем абсолютным
        if "database('database.sqlite')" in output or "'database.sqlite'" in output:
            print("Исправляю путь на абсолютный...")
            conn.execute(f"sed -i \"s|'database' => database('database.sqlite')|'database' => database_path('database.sqlite')|g\" {config_file}")
            conn.execute(f"sed -i \"s|'database' => 'database.sqlite'|'database' => database_path('database.sqlite')|g\" {config_file}")

def main():
    """Главная функция"""
    print("="*60)
    print("🔧 Исправление конфигурации базы данных")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        check_database_config(conn)
        fix_database_path(conn)
        
        # Очищаем кэш конфигурации
        print("\n🧹 Очистка кэша конфигурации...")
        conn.execute("cd /root/shannon/backend-laravel && php artisan config:clear")
        
        # Тестируем подключение
        if test_database_connection(conn):
            # Перезапускаем Laravel
            print("\n🔄 Перезапуск Laravel...")
            conn.execute("systemctl restart shannon-laravel")
            
            import time
            time.sleep(3)
            
            print("✅ Готово")
        else:
            print("\n❌ Не удалось исправить подключение")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


