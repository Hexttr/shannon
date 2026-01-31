#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальное развертывание
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
    print("ФИНАЛЬНОЕ РАЗВЕРТЫВАНИЕ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Обновление
        print("\n1. ОБНОВЛЕНИЕ:")
        ssh_exec(ssh, "cd /root/shannon && git pull")
        
        # 2. Очистка
        print("\n2. ОЧИСТКА:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan optimize:clear 2>&1")
        
        # 3. Перезапуск
        print("\n3. ПЕРЕЗАПУСК:")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service")
        time.sleep(4)
        
        # 4. Тест
        print("\n4. ТЕСТ API:")
        success, output, error = ssh_exec(ssh, "curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}'")
        print(f"  Ответ: {output[:400]}")
        
        if "token" in output.lower():
            print("  [OK] API РАБОТАЕТ!")
        elif "validation" in output.lower() or "username" in output.lower():
            print("  [OK] API отвечает (ошибка валидации - нормально)")
        else:
            print("  [WARNING] Проверьте логи")
            ssh_exec(ssh, f"tail -30 {BACKEND_DIR}/storage/logs/laravel.log")
        
        print("\n" + "="*60)
        print("РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО")
        print("="*60)
        print(f"\nПриложение: http://{SSH_HOST}")
        print(f"Логин: admin")
        print(f"Пароль: admin")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

