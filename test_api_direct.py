#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Прямое тестирование API
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
    print("ПРЯМОЕ ТЕСТИРОВАНИЕ API")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Тест напрямую на порт 8000
        print("\n1. ТЕСТ НАПРЯМУЮ НА ПОРТ 8000:")
        success, output, error = ssh_exec(ssh, "curl -v http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' 2>&1")
        print(output[-500:])
        
        # 2. Проверка логов Laravel
        print("\n2. ЛОГИ LARAVEL:")
        success, output, error = ssh_exec(ssh, f"tail -30 {BACKEND_DIR}/storage/logs/laravel.log 2>&1")
        print(output[-600:])
        
        # 3. Проверка маршрутов
        print("\n3. МАРШРУТЫ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan route:list | grep auth")
        print(output)
        
        # 4. Тест через Nginx
        print("\n4. ТЕСТ ЧЕРЕЗ NGINX:")
        success, output, error = ssh_exec(ssh, f"curl -v http://{SSH_HOST}/api/auth/login -X POST -H 'Content-Type: application/json' -d '{{\"username\":\"admin\",\"password\":\"admin\"}}' 2>&1 | grep -E '(HTTP|Location|Content-Type)'")
        print(output)
        
        print("\n" + "="*60)
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("="*60)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

