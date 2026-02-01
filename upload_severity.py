#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка severity.ts на сервер
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
    sftp = ssh.open_sftp()
    
    try:
        # Создаем директорию utils
        print("1. СОЗДАНИЕ ДИРЕКТОРИИ:")
        ssh_exec(ssh, f"mkdir -p {FRONTEND_DIR}/src/utils")
        print("  [OK] Директория создана")
        
        # Загружаем файл
        print("\n2. ЗАГРУЗКА ФАЙЛА:")
        f = open('template/src/utils/severity.ts', 'rb')
        sftp.putfo(f, f'{FRONTEND_DIR}/src/utils/severity.ts')
        f.close()
        print("  [OK] Файл загружен")
        
    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    main()



