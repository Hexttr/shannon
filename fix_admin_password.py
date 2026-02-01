#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление пароля администратора
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def fix_admin_password():
    """Исправляет пароль администратора"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔧 Исправление пароля администратора...")
        print("="*60)
        
        # Проверяем текущего пользователя
        print("\n1. Проверка текущего пользователя...")
        check_cmd = """cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$user = App\\\\Models\\\\User::where('username', 'admin')->first();
if (\$user) {
    echo 'User found: ' . \$user->username . PHP_EOL;
    echo 'Has password: ' . (\$user->password ? 'yes' : 'no') . PHP_EOL;
    echo 'Password hash: ' . substr(\$user->password, 0, 20) . '...' . PHP_EOL;
} else {
    echo 'User not found' . PHP_EOL;
}
" 2>&1"""
        
        output, _, _ = conn.execute(check_cmd)
        print(output)
        
        # Обновляем пароль
        print("\n2. Обновление пароля на 'admin'...")
        update_cmd = """cd /root/shannon/backend-laravel && php artisan tinker --execute="
use Illuminate\\\\Support\\\\Facades\\\\Hash;
\$user = App\\\\Models\\\\User::where('username', 'admin')->first();
if (\$user) {
    \$user->password = Hash::make('admin');
    \$user->save();
    echo 'Password updated successfully!' . PHP_EOL;
} else {
    echo 'User not found, creating new user...' . PHP_EOL;
    \$user = App\\\\Models\\\\User::create([
        'id' => Illuminate\\\\Support\\\\Str::uuid(),
        'username' => 'admin',
        'email' => 'admin@shannon.local',
        'password' => Hash::make('admin'),
    ]);
    echo 'User created successfully!' . PHP_EOL;
}
" 2>&1"""
        
        output, _, _ = conn.execute(update_cmd)
        print(output)
        
        # Проверяем что пароль работает
        print("\n3. Тестирование логина...")
        test_cmd = """curl -s -X POST http://localhost:8000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -H "Accept: application/json" \\
  -d '{"username":"admin","password":"admin"}'"""
        
        output, error, code = conn.execute(test_cmd)
        print(f"Exit code: {code}")
        print(f"Response: {output}")
        
        if 'token' in output:
            print("\n✅ Пароль успешно исправлен! Логин работает.")
            return True
        else:
            print("\n❌ Логин все еще не работает. Проверьте ответ выше.")
            return False
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = fix_admin_password()
    sys.exit(0 if success else 1)

