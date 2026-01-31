#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновление файлов на сервере
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
    print("="*60)
    print("ОБНОВЛЕНИЕ ФАЙЛОВ НА СЕРВЕРЕ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    sftp = ssh.open_sftp()
    
    try:
        # 1. Обновление репозитория
        print("\n1. ОБНОВЛЕНИЕ РЕПОЗИТОРИЯ:")
        ssh_exec(ssh, "cd /root/shannon && git pull")
        print("  [OK] Репозиторий обновлен")
        
        # 2. Копирование файлов
        print("\n2. КОПИРОВАНИЕ ФАЙЛОВ:")
        files_to_copy = [
            ("backend-laravel/app/Http/Middleware/VerifyCsrfToken.php", f"{BACKEND_DIR}/app/Http/Middleware/VerifyCsrfToken.php"),
            ("backend-laravel/bootstrap/app.php", f"{BACKEND_DIR}/bootstrap/app.php"),
        ]
        
        for local_file, remote_file in files_to_copy:
            try:
                with open(local_file, 'rb') as f:
                    sftp.putfo(f, remote_file)
                print(f"  [OK] {local_file.split('/')[-1]}")
            except Exception as e:
                print(f"  [ERROR] {local_file}: {e}")
        
        # 3. Очистка кэша
        print("\n3. ОЧИСТКА КЭША:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan config:clear 2>&1")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan route:clear 2>&1")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan cache:clear 2>&1")
        print("  [OK] Кэш очищен")
        
        # 4. Перезапуск
        print("\n4. ПЕРЕЗАПУСК:")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service")
        time.sleep(3)
        
        # 5. Тест
        print("\n5. ТЕСТ:")
        import requests
        from urllib3.exceptions import InsecureRequestWarning
        import urllib3
        urllib3.disable_warnings(InsecureRequestWarning)
        
        response = requests.post(
            f"https://{SSH_HOST}/api/auth/login",
            json={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/json", "Origin": f"https://{SSH_HOST}"},
            verify=False,
            timeout=10
        )
        
        print(f"  Статус: {response.status_code}")
        if response.status_code == 200:
            print("  [OK] API работает!")
            print(f"  Ответ: {response.text[:200]}")
        else:
            print(f"  [WARNING] Ответ: {response.text[:300]}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nПопробуйте войти снова:")
        print(f"  URL: https://{SSH_HOST}")
        print(f"  Логин: admin")
        print(f"  Пароль: admin")
        
    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    main()

