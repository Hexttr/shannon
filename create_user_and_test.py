#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание пользователя и проверка работоспособности
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
    """Выполняет команду на сервере"""
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    print("="*60)
    print("СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ И ПРОВЕРКА")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка статуса сервиса
        print("\n1. ПРОВЕРКА СТАТУСА BACKEND:")
        success, output, error = ssh_exec(ssh, "systemctl is-active shannon-laravel.service")
        if success and "active" in output.lower():
            print("  [OK] Backend сервис запущен")
        else:
            print(f"  [WARNING] Статус: {output.strip()}")
            ssh_exec(ssh, "systemctl restart shannon-laravel.service")
            time.sleep(2)
        
        # 2. Проверка доступности API
        print("\n2. ПРОВЕРКА API:")
        success, output, error = ssh_exec(ssh, "curl -s http://localhost:8000/up")
        if success and "ok" in output.lower():
            print("  [OK] API доступен")
        else:
            print(f"  [WARNING] Ответ: {output[:100]}")
        
        # 3. Проверка существующих пользователей
        print("\n3. ПРОВЕРКА ПОЛЬЗОВАТЕЛЕЙ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan tinker --execute=\"echo \\App\\Models\\User::count();\" 2>&1")
        user_count = output.strip()
        if user_count.isdigit() and int(user_count) > 0:
            print(f"  [OK] Найдено пользователей: {user_count}")
            print("  Пропускаем создание пользователя")
        else:
            print("  Создание пользователя admin...")
            # Создаем пользователя через tinker
            create_user_cmd = f"""cd {BACKEND_DIR} && php artisan tinker --execute="
\\$user = \\App\\Models\\User::create([
    'id' => \\Illuminate\\Support\\Str::uuid(),
    'username' => 'admin',
    'email' => 'admin@shannon.local',
    'password' => \\Illuminate\\Support\\Facades\\Hash::make('admin'),
]);
echo 'User created: ' . \\$user->username;
" 2>&1"""
            
            success, output, error = ssh_exec(ssh, create_user_cmd)
            if success or "User created" in output:
                print("  [OK] Пользователь создан")
                print(f"  Логин: admin")
                print(f"  Пароль: admin")
            else:
                print(f"  [WARNING] Возможны ошибки: {output[-200:]}")
                print("  Создайте пользователя вручную через tinker")
        
        # 4. Проверка frontend
        print("\n4. ПРОВЕРКА FRONTEND:")
        success, output, error = ssh_exec(ssh, "ls -la /root/shannon/template/dist/index.html 2>&1")
        if success:
            print("  [OK] Frontend собран")
        else:
            print("  [WARNING] Frontend не собран, запускаем сборку...")
            ssh_exec(ssh, "cd /root/shannon/template && npm run build 2>&1 | tail -5")
        
        # 5. Проверка Nginx
        print("\n5. ПРОВЕРКА NGINX:")
        success, output, error = ssh_exec(ssh, "nginx -t 2>&1")
        if "successful" in output.lower():
            print("  [OK] Nginx конфигурация валидна")
        else:
            print(f"  [ERROR] Ошибка Nginx: {output}")
        
        # 6. Финальная проверка
        print("\n6. ФИНАЛЬНАЯ ПРОВЕРКА:")
        print(f"  Frontend: http://{SSH_HOST}")
        print(f"  API: http://{SSH_HOST}/api")
        print(f"  Health: http://{SSH_HOST}/up")
        
        success, output, error = ssh_exec(ssh, f"curl -s http://{SSH_HOST}/up")
        if "ok" in output.lower():
            print("  [OK] Приложение доступно через Nginx")
        else:
            print(f"  [WARNING] Проверьте Nginx: {output[:100]}")
        
        print("\n" + "="*60)
        print("ГОТОВО К ИСПОЛЬЗОВАНИЮ!")
        print("="*60)
        print(f"\nВойдите в приложение:")
        print(f"  URL: http://{SSH_HOST}")
        print(f"  Логин: admin")
        print(f"  Пароль: admin")
        print(f"\nЕсли пользователь не создан, выполните:")
        print(f"  ssh {SSH_USER}@{SSH_HOST}")
        print(f"  cd {BACKEND_DIR}")
        print(f"  php artisan tinker")
        print(f"  \\App\\Models\\User::create([")
        print(f"    'id' => \\Illuminate\\Support\\Str::uuid(),")
        print(f"    'username' => 'admin',")
        print(f"    'email' => 'admin@test.com',")
        print(f"    'password' => \\Illuminate\\Support\\Facades\\Hash::make('admin'),")
        print(f"  ]);")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

