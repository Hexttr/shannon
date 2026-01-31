#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка и исправление проблем на сервере
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
    print("ПРОВЕРКА И ИСПРАВЛЕНИЕ ПРОБЛЕМ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка логов backend
        print("\n1. ПРОВЕРКА ЛОГОВ BACKEND:")
        success, output, error = ssh_exec(ssh, "journalctl -u shannon-laravel.service -n 30 --no-pager")
        print(output[-500:])
        
        # 2. Перезапуск backend
        print("\n2. ПЕРЕЗАПУСК BACKEND:")
        ssh_exec(ssh, "systemctl stop shannon-laravel.service")
        time.sleep(2)
        ssh_exec(ssh, "systemctl start shannon-laravel.service")
        time.sleep(3)
        
        success, output, error = ssh_exec(ssh, "systemctl status shannon-laravel.service --no-pager -l | head -20")
        print(output)
        
        # 3. Проверка доступности
        print("\n3. ПРОВЕРКА ДОСТУПНОСТИ:")
        time.sleep(2)
        success, output, error = ssh_exec(ssh, "curl -s http://localhost:8000/api/auth/login")
        print(f"  API ответ: {output[:200]}")
        
        success, output, error = ssh_exec(ssh, "curl -s http://localhost:8000/")
        print(f"  Root ответ: {output[:200]}")
        
        # 4. Проверка маршрутов
        print("\n4. ПРОВЕРКА МАРШРУТОВ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan route:list | grep -E '(auth|api)' | head -10")
        print(output)
        
        # 5. Проверка frontend
        print("\n5. ПРОВЕРКА FRONTEND:")
        success, output, error = ssh_exec(ssh, "curl -s http://localhost/ | head -20")
        if "<!DOCTYPE html>" in output or "<html" in output.lower():
            print("  [OK] Frontend доступен")
        else:
            print(f"  [WARNING] Ответ: {output[:200]}")
        
        # 6. Проверка через внешний IP
        print("\n6. ПРОВЕРКА ЧЕРЕЗ ВНЕШНИЙ IP:")
        print(f"  Откройте в браузере: http://{SSH_HOST}")
        print(f"  Должна открыться страница входа")
        
        print("\n" + "="*60)
        print("ПРОВЕРКА ЗАВЕРШЕНА")
        print("="*60)
        print(f"\nВойдите в приложение:")
        print(f"  URL: http://{SSH_HOST}")
        print(f"  Логин: admin")
        print(f"  Пароль: admin")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

