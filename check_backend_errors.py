#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка ошибок Laravel backend
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
    print("ПРОВЕРКА ОШИБОК BACKEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка логов Laravel
        print("\n1. ЛОГИ LARAVEL:")
        success, output, error = ssh_exec(ssh, f"tail -50 {BACKEND_DIR}/storage/logs/laravel.log 2>&1")
        print(output[-800:])
        
        # 2. Проверка конфигурации
        print("\n2. ПРОВЕРКА КОНФИГУРАЦИИ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan config:clear 2>&1")
        print("  Конфигурация очищена")
        
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan route:clear 2>&1")
        print("  Маршруты очищены")
        
        # 3. Проверка маршрутов
        print("\n3. ПРОВЕРКА МАРШРУТОВ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan route:list 2>&1 | head -20")
        print(output)
        
        # 4. Проверка .env
        print("\n4. ПРОВЕРКА .ENV:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && grep -E '^(APP_|DB_)' .env | head -10")
        print(output)
        
        # 5. Тест API напрямую
        print("\n5. ТЕСТ API:")
        success, output, error = ssh_exec(ssh, "curl -v http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"test\",\"password\":\"test\"}' 2>&1 | head -30")
        print(output)
        
        # 6. Перезапуск с очисткой кэша
        print("\n6. ПЕРЕЗАПУСК С ОЧИСТКОЙ:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan optimize:clear 2>&1")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service")
        
        import time
        time.sleep(3)
        
        success, output, error = ssh_exec(ssh, "systemctl status shannon-laravel.service --no-pager | head -10")
        print(output)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

