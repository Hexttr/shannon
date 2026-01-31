#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка ошибки 500
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
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Очистка логов и тестовый запрос
        ssh_exec(ssh, f"echo '' > {BACKEND_DIR}/storage/logs/laravel.log")
        
        import requests
        from urllib3.exceptions import InsecureRequestWarning
        import urllib3
        urllib3.disable_warnings(InsecureRequestWarning)
        
        requests.post(
            f"https://{SSH_HOST}/api/auth/login",
            json={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/json", "Origin": f"https://{SSH_HOST}"},
            verify=False,
            timeout=10
        )
        
        time.sleep(1)
        
        # Чтение логов
        success, output, error = ssh_exec(ssh, f"cat {BACKEND_DIR}/storage/logs/laravel.log")
        print(output[-2000:])
        
        # Проверка статуса сервиса
        print("\nСТАТУС СЕРВИСА:")
        success, output, error = ssh_exec(ssh, "systemctl status shannon-laravel.service --no-pager | head -15")
        print(output)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

