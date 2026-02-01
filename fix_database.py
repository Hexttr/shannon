#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление проблемы с базой данных
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def fix_database(conn):
    """Создает базу данных и выполняет миграции"""
    print("\n" + "="*60)
    print("🔧 Исправление базы данных...")
    print("="*60)
    
    db_path = "/root/shannon/backend-laravel/database/database.sqlite"
    db_dir = "/root/shannon/backend-laravel/database"
    
    # Проверяем существование директории
    output, error, code = conn.execute(f"test -d {db_dir} && echo 'exists' || echo 'not-found'")
    if 'not-found' in output:
        print(f"📁 Создание директории {db_dir}...")
        conn.execute(f"mkdir -p {db_dir}")
    
    # Создаем пустой файл базы данных
    print(f"\n💾 Создание файла базы данных...")
    output, error, code = conn.execute(f"touch {db_path}")
    if code == 0:
        print("✅ Файл базы данных создан")
    else:
        print(f"❌ Ошибка создания файла: {error}")
        return False
    
    # Устанавливаем права доступа
    print("\n🔐 Установка прав доступа...")
    conn.execute(f"chmod 664 {db_path}")
    conn.execute(f"chown www-data:www-data {db_path} 2>/dev/null || chown root:root {db_path}")
    
    # Выполняем миграции
    print("\n🔄 Выполнение миграций...")
    output, error, code = conn.execute("cd /root/shannon/backend-laravel && php artisan migrate --force 2>&1")
    
    if code == 0:
        print("✅ Миграции выполнены успешно")
        if output:
            print(f"\n   {output[-500:]}")
        return True
    else:
        print(f"❌ Ошибка выполнения миграций:")
        print(f"   {error}")
        if output:
            print(f"   {output[-500:]}")
        return False

def check_database(conn):
    """Проверяет базу данных"""
    print("\n" + "="*60)
    print("🔍 Проверка базы данных...")
    print("="*60)
    
    db_path = "/root/shannon/backend-laravel/database/database.sqlite"
    
    # Проверяем существование файла
    output, error, code = conn.execute(f"test -f {db_path} && echo 'exists' || echo 'not-found'")
    if 'exists' in output:
        # Проверяем размер файла
        output, error, code = conn.execute(f"ls -lh {db_path} | awk '{{print $5}}'")
        if output:
            print(f"✅ База данных существует, размер: {output.strip()}")
        
        # Проверяем таблицы
        output, error, code = conn.execute(f"cd /root/shannon/backend-laravel && php artisan db:show 2>&1")
        if 'tables' in output.lower() or 'users' in output.lower():
            print("✅ Таблицы созданы")
            print(f"\n   {output[:300]}")
        else:
            print("⚠️  Не удалось проверить таблицы")
    else:
        print("❌ База данных не найдена")

def main():
    """Главная функция"""
    print("="*60)
    print("🔧 Исправление проблемы с базой данных")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        # Исправление базы данных
        if fix_database(conn):
            # Проверка
            check_database(conn)
            
            print("\n" + "="*60)
            print("✅ База данных исправлена")
            print("="*60)
            print("\n💡 Рекомендуется перезапустить Laravel сервис:")
            print("   systemctl restart shannon-laravel")
        else:
            print("\n" + "="*60)
            print("❌ Не удалось исправить базу данных")
            print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


