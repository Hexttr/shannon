#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновление Laravel backend на сервере
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
    print("ОБНОВЛЕНИЕ BACKEND НА СЕРВЕРЕ")
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
        
        # 2. Копирование недостающих файлов
        print("\n2. КОПИРОВАНИЕ ФАЙЛОВ:")
        controller_file = "backend-laravel/app/Http/Controllers/Controller.php"
        if Path(controller_file).exists():
            print("  Копирую Controller.php...")
            sftp.put(controller_file, f"{BACKEND_DIR}/app/Http/Controllers/Controller.php")
        
        # 3. Очистка кэша
        print("\n3. ОЧИСТКА КЭША:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan optimize:clear 2>&1")
        
        # 4. Перезапуск
        print("\n4. ПЕРЕЗАПУСК:")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service")
        
        import time
        time.sleep(3)
        
        success, output, error = ssh_exec(ssh, "systemctl status shannon-laravel.service --no-pager | head -10")
        print(output)
        
        # 5. Проверка
        print("\n5. ПРОВЕРКА:")
        success, output, error = ssh_exec(ssh, "curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{}'")
        if "validation" in output.lower() or "username" in output.lower():
            print("  [OK] API работает!")
        else:
            print(f"  [WARNING] Ответ: {output[:200]}")
        
    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    from pathlib import Path
    main()

