#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание пользователя в базе данных
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def create_user(conn):
    """Создает пользователя через seeder"""
    print("\n" + "="*60)
    print("👤 Создание пользователя...")
    print("="*60)
    
    # Запускаем seeder
    print("\n🔄 Запуск UserSeeder...")
    output, error, code = conn.execute("cd /root/shannon/backend-laravel && php artisan db:seed --class=UserSeeder 2>&1")
    
    if code == 0:
        print("✅ Пользователь создан")
        if output:
            print(f"\n   {output}")
        return True
    else:
        print(f"⚠️  Seeder не выполнился или пользователь уже существует")
        if output:
            print(f"   {output}")
        
        # Пытаемся создать пользователя через tinker
        print("\n🔄 Попытка создать пользователя через tinker...")
        tinker_cmd = """
php artisan tinker --execute="
\$user = App\\\\Models\\\\User::firstOrCreate(
    ['username' => 'admin'],
    [
        'email' => 'admin@shannon.local',
        'password' => bcrypt('admin123'),
        'email_verified_at' => now()
    ]
);
echo 'User created: ' . \$user->username;
"
"""
        output, error, code = conn.execute(f"cd /root/shannon/backend-laravel && {tinker_cmd} 2>&1")
        
        if code == 0 and 'created' in output.lower():
            print("✅ Пользователь создан через tinker")
            print(f"   {output}")
            return True
        else:
            print(f"⚠️  Не удалось создать пользователя")
            if output:
                print(f"   {output}")
            return False

def verify_user(conn):
    """Проверяет созданного пользователя"""
    print("\n" + "="*60)
    print("🔍 Проверка пользователя...")
    print("="*60)
    
    output, error, code = conn.execute("cd /root/shannon/backend-laravel && php artisan tinker --execute=\"echo App\\\\Models\\\\User::count();\" 2>&1")
    if output:
        try:
            count = int(output.strip())
            if count > 0:
                print(f"✅ Пользователей в базе: {count}")
                
                # Показываем список пользователей
                output2, error2, code2 = conn.execute("cd /root/shannon/backend-laravel && php artisan tinker --execute=\"App\\\\Models\\\\User::all(['username', 'email'])->each(fn(\\$u) => print(\\$u->username . ' (' . \\$u->email . ')' . PHP_EOL));\" 2>&1")
                if output2:
                    print("\n📋 Пользователи:")
                    print(output2)
                
                return True
        except:
            pass
    
    print("⚠️  Не удалось проверить пользователей")
    return False

def main():
    """Главная функция"""
    print("="*60)
    print("👤 Создание пользователя")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        # Создание пользователя
        create_user(conn)
        
        # Проверка
        verify_user(conn)
        
        print("\n" + "="*60)
        print("✅ Готово")
        print("="*60)
        print("\n💡 Учетные данные по умолчанию:")
        print("   Username: admin")
        print("   Password: admin123")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


