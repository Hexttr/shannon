#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка ошибки логина 422
"""

import paramiko
import sys
import time
import requests
from urllib3.exceptions import InsecureRequestWarning
import urllib3

urllib3.disable_warnings(InsecureRequestWarning)

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
    print("ПРОВЕРКА ОШИБКИ ЛОГИНА 422")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Очистка логов и тестовый запрос
        print("\n1. ТЕСТОВЫЙ ЗАПРОС:")
        ssh_exec(ssh, f"echo '' > {BACKEND_DIR}/storage/logs/laravel.log")
        
        # Делаем запрос как frontend
        response = requests.post(
            f"https://{SSH_HOST}/api/auth/login",
            json={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/json"},
            verify=False,
            timeout=10
        )
        
        print(f"  Статус: {response.status_code}")
        print(f"  Ответ: {response.text[:500]}")
        
        time.sleep(1)
        
        # 2. Проверка логов Laravel
        print("\n2. ЛОГИ LARAVEL:")
        success, output, error = ssh_exec(ssh, f"cat {BACKEND_DIR}/storage/logs/laravel.log")
        print(output[-1500:])
        
        # 3. Проверка CORS
        print("\n3. ПРОВЕРКА CORS:")
        success, output, error = ssh_exec(ssh, f"cat {BACKEND_DIR}/config/cors.php | grep -A 10 'allowed_origins'")
        print(output)
        
        # 4. Проверка маршрутов
        print("\n4. ПРОВЕРКА МАРШРУТОВ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan route:list | grep auth")
        print(output)
        
        # 5. Проверка LoginRequest
        print("\n5. ПРОВЕРКА LOGINREQUEST:")
        success, output, error = ssh_exec(ssh, f"cat {BACKEND_DIR}/app/Http/Requests/LoginRequest.php")
        print(output)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

