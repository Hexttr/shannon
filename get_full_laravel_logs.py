#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Получение полных логов Laravel
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
    print("ПОЛНЫЕ ЛОГИ LARAVEL")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Получаем последние логи
        print("\nПОСЛЕДНИЕ ОШИБКИ:")
        success, output, error = ssh_exec(ssh, f"tail -100 {BACKEND_DIR}/storage/logs/laravel.log 2>&1 | grep -A 20 'ERROR' | tail -50")
        print(output)
        
        # Пробуем сделать запрос и сразу смотрим логи
        print("\n" + "="*60)
        print("ДЕЛАЕМ ЗАПРОС И СМОТРИМ ЛОГИ:")
        ssh_exec(ssh, f"curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{{\"username\":\"test\",\"password\":\"test\"}}' > /dev/null")
        import time
        time.sleep(1)
        success, output, error = ssh_exec(ssh, f"tail -50 {BACKEND_DIR}/storage/logs/laravel.log 2>&1")
        print(output[-1000:])
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

