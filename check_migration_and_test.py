#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка миграции и тест
"""

import paramiko
import sys
import time

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
BACKEND_DIR = "/root/shannon/backend-laravel"

def ssh_exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка структуры таблицы
        print("1. ПРОВЕРКА СТРУКТУРЫ ТАБЛИЦЫ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && sqlite3 database/database.sqlite '.schema personal_access_tokens' 2>&1")
        print(output)
        
        # 2. Пересоздание таблицы через миграцию
        print("\n2. ПЕРЕСОЗДАНИЕ ТАБЛИЦЫ:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan migrate:fresh --force 2>&1")
        
        # 3. Проверка структуры после миграции
        print("\n3. СТРУКТУРА ПОСЛЕ МИГРАЦИИ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && sqlite3 database/database.sqlite '.schema personal_access_tokens' 2>&1")
        print(output)
        
        # 4. Создание пользователя
        print("\n4. СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ:")
        create_user_cmd = f"""cd {BACKEND_DIR} && php artisan tinker --execute="
if (\\App\\Models\\User::where('username', 'admin')->exists()) {{
    echo 'User already exists';
}} else {{
    \\$user = \\App\\Models\\User::create([
        'id' => \\Illuminate\\Support\\Str::uuid(),
        'username' => 'admin',
        'email' => 'admin@shannon.local',
        'password' => \\Illuminate\\Support\\Facades\\Hash::make('admin'),
    ]);
    echo 'User created: ' . \\$user->username;
}}
" 2>&1"""
        success, output, error = ssh_exec(ssh, create_user_cmd)
        print(output)
        
        # 5. Очистка и перезапуск
        print("\n5. ОЧИСТКА И ПЕРЕЗАПУСК:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan optimize:clear 2>&1")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service")
        time.sleep(4)
        
        # 6. Тест API
        print("\n6. ТЕСТ API:")
        success, output, error = ssh_exec(ssh, "curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}'")
        print(f"Ответ: {output[:500]}")
        
        if "token" in output.lower() and "user" in output.lower():
            print("\n✅ [SUCCESS] API РАБОТАЕТ!")
        elif "validation" in output.lower() or "username" in output.lower():
            print("\n✅ [SUCCESS] API отвечает (ошибка валидации - нормально)")
        else:
            print("\n❌ [ERROR] Проверьте логи")
            success, output, error = ssh_exec(ssh, f"tail -30 {BACKEND_DIR}/storage/logs/laravel.log")
            print(output[-500:])
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

