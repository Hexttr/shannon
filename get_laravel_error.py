#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Получение полной ошибки из Laravel
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
    print("ПОЛУЧЕНИЕ ОШИБКИ ИЗ LARAVEL")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Делаем запрос чтобы создать новую ошибку в логах
        print("\n1. СОЗДАНИЕ ЗАПРОСА:")
        ssh_exec(ssh, "curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' > /dev/null")
        
        import time
        time.sleep(1)
        
        # Получаем последние ошибки
        print("\n2. ПОСЛЕДНИЕ ОШИБКИ:")
        success, output, error = ssh_exec(ssh, f"tail -100 {BACKEND_DIR}/storage/logs/laravel.log 2>&1 | grep -A 30 'ERROR' | tail -50")
        if output:
            print(output)
        else:
            # Если нет ERROR, берем последние строки
            success, output, error = ssh_exec(ssh, f"tail -80 {BACKEND_DIR}/storage/logs/laravel.log 2>&1")
            print(output[-1500:])
        
        # Получаем полный стек трейс последней ошибки
        print("\n3. ПОЛНЫЙ СТЕК ТРЕЙС:")
        success, output, error = ssh_exec(ssh, f"tail -200 {BACKEND_DIR}/storage/logs/laravel.log 2>&1 | grep -B 5 -A 50 'Exception' | tail -60")
        print(output[-2000:])
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

