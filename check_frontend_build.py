#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка сборки frontend
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
        # Проверка dist
        print("1. ПРОВЕРКА DIST:")
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ | head -15")
        print(output)
        
        # Проверка index.html
        print("\n2. ПРОВЕРКА INDEX.HTML:")
        success, output, error = ssh_exec(ssh, f"head -20 {FRONTEND_DIR}/dist/index.html")
        print(output)
        
        # Проверка наличия новых файлов
        print("\n3. ПРОВЕРКА ASSETS:")
        success, output, error = ssh_exec(ssh, f"ls -lt {FRONTEND_DIR}/dist/assets/ | head -5")
        print(output)
        
        # Тест доступа
        print("\n4. ТЕСТ ДОСТУПА:")
        success, output, error = ssh_exec(ssh, f"curl -k -s https://{SSH_HOST}/ | head -20")
        if "<!DOCTYPE html>" in output or "<html" in output.lower():
            print("  [OK] Frontend доступен")
            print(f"  {output[:200]}")
        else:
            print(f"  [WARNING] Ответ: {output[:300]}")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

