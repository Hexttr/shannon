#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка ошибок Nginx
"""

import paramiko
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
FRONTEND_DIR = "/root/shannon/template"

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
        # 1. Проверка логов Nginx
        print("1. ЛОГИ NGINX:")
        success, output, error = ssh_exec(ssh, "tail -30 /var/log/nginx/error.log")
        print(output[-800:])
        
        # 2. Проверка конфигурации
        print("\n2. КОНФИГУРАЦИЯ NGINX:")
        success, output, error = ssh_exec(ssh, "cat /etc/nginx/sites-available/shannon")
        print(output)
        
        # 3. Проверка существования файлов
        print("\n3. ПРОВЕРКА ФАЙЛОВ:")
        success, output, error = ssh_exec(ssh, f"test -f {FRONTEND_DIR}/dist/index.html && echo 'EXISTS' || echo 'MISSING'")
        print(f"  index.html: {output.strip()}")
        
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/")
        print(output)
        
        # 4. Тест чтения файла
        print("\n4. ТЕСТ ЧТЕНИЯ ФАЙЛА:")
        success, output, error = ssh_exec(ssh, f"cat {FRONTEND_DIR}/dist/index.html | head -10")
        print(output)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

