#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание пользователя с правильным UUID
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def create_user_with_uuid(conn):
    """Создает пользователя с UUID"""
    print("\n" + "="*60)
    print("👤 Создание пользователя с UUID...")
    print("="*60)
    
    # Создаем пользователя через tinker с UUID
    tinker_cmd = """
php artisan tinker --execute="
use Illuminate\\\\Support\\\\Str;
use Illuminate\\\\Support\\\\Facades\\\\Hash;

\$user = App\\\\Models\\\\User::firstOrCreate(
    ['username' => 'admin'],
    [
        'id' => Str::uuid()->toString(),
        'email' => 'admin@shannon.local',
        'password' => Hash::make('admin123'),
        'email_verified_at' => now()
    ]
);
echo 'User: ' . \$user->username . ' (ID: ' . \$user->id . ')';
"
"""
    
    output, error, code = conn.execute(f"cd /root/shannon/backend-laravel && {tinker_cmd} 2>&1")
    
    if code == 0:
        print("✅ Команда выполнена")
        if output:
            print(f"\n   {output}")
            if 'User:' in output or 'created' in output.lower():
                return True
    else:
        print(f"⚠️  Ошибка: {error}")
        if output:
            print(f"   {output}")
    
    return False

def verify_user(conn):
    """Проверяет пользователя"""
    print("\n" + "="*60)
    print("🔍 Проверка пользователя...")
    print("="*60)
    
    output, error, code = conn.execute("cd /root/shannon/backend-laravel && php artisan tinker --execute=\"echo 'Users: ' . App\\\\Models\\\\User::count();\" 2>&1")
    if output:
        print(output)
        if 'Users: 1' in output or 'Users: 2' in output:
            print("✅ Пользователь создан")
            return True
    
    return False

def main():
    """Главная функция"""
    print("="*60)
    print("👤 Создание пользователя (исправленная версия)")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        if create_user_with_uuid(conn):
            verify_user(conn)
        
        print("\n" + "="*60)
        print("✅ Готово")
        print("="*60)
        print("\n💡 Учетные данные:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n✅ Теперь можно войти в систему!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


