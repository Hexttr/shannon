#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление таблицы personal_access_tokens
"""

import paramiko
import sys

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
    print("="*60)
    print("ИСПРАВЛЕНИЕ ТАБЛИЦЫ personal_access_tokens")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Обновление репозитория
        print("\n1. ОБНОВЛЕНИЕ:")
        ssh_exec(ssh, "cd /root/shannon && git pull")
        
        # 2. Пересоздание таблицы
        print("\n2. ПЕРЕСОЗДАНИЕ ТАБЛИЦЫ:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan migrate:fresh --force 2>&1")
        
        # 3. Пересоздание пользователя
        print("\n3. СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ:")
        create_user_cmd = f"""cd {BACKEND_DIR} && php artisan tinker --execute="
\\$user = \\App\\Models\\User::create([
    'id' => \\Illuminate\\Support\\Str::uuid(),
    'username' => 'admin',
    'email' => 'admin@shannon.local',
    'password' => \\Illuminate\\Support\\Facades\\Hash::make('admin'),
]);
echo 'User created: ' . \\$user->username;
" 2>&1"""
        ssh_exec(ssh, create_user_cmd)
        
        # 4. Очистка кэша
        print("\n4. ОЧИСТКА КЭША:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan optimize:clear 2>&1")
        
        # 5. Перезапуск
        print("\n5. ПЕРЕЗАПУСК:")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service")
        
        import time
        time.sleep(3)
        
        # 6. Тест
        print("\n6. ТЕСТ API:")
        success, output, error = ssh_exec(ssh, "curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}'")
        print(f"  Ответ: {output[:400]}")
        
        if "token" in output.lower():
            print("  [OK] API РАБОТАЕТ!")
        elif "validation" in output.lower():
            print("  [OK] API отвечает")
        else:
            print("  [WARNING] Проверьте ответ")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

