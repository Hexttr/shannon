#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление проблемы с trust project в Laravel
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
    print("ИСПРАВЛЕНИЕ TRUST PROJECT")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Доверяем проекту
        print("\n1. ДОВЕРИЕ ПРОЕКТУ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan trust-project --force 2>&1")
        print(output)
        
        # 2. Очистка кэша
        print("\n2. ОЧИСТКА КЭША:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan optimize:clear 2>&1")
        
        # 3. Перезапуск
        print("\n3. ПЕРЕЗАПУСК:")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service")
        time.sleep(3)
        
        # 4. Проверка
        print("\n4. ПРОВЕРКА:")
        success, output, error = ssh_exec(ssh, "systemctl status shannon-laravel.service --no-pager | head -10")
        print(output)
        
        # 5. Тест API
        print("\n5. ТЕСТ API:")
        time.sleep(2)
        success, output, error = ssh_exec(ssh, "curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}'")
        print(f"  Ответ: {output[:300]}")
        
        if "token" in output.lower() or "user" in output.lower():
            print("  [OK] API работает!")
        elif "validation" in output.lower():
            print("  [OK] API отвечает (ошибка валидации - это нормально)")
        else:
            print(f"  [WARNING] Неожиданный ответ")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

