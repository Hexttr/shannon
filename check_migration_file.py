#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка файла миграции на сервере
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
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Обновление репозитория
        print("1. ОБНОВЛЕНИЕ РЕПОЗИТОРИЯ:")
        ssh_exec(ssh, "cd /root/shannon && git pull")
        
        # Проверка файла миграции
        print("\n2. ПРОВЕРКА ФАЙЛА МИГРАЦИИ:")
        success, output, error = ssh_exec(ssh, f"cat {BACKEND_DIR}/database/migrations/2024_01_01_000006_create_personal_access_tokens_table.php")
        print(output)
        
        # Удаление записи и таблицы
        print("\n3. УДАЛЕНИЕ И ПЕРЕСОЗДАНИЕ:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && sqlite3 database/database.sqlite \"DELETE FROM migrations WHERE migration = '2024_01_01_000006_create_personal_access_tokens_table';\" 2>&1")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && sqlite3 database/database.sqlite 'DROP TABLE IF EXISTS personal_access_tokens;' 2>&1")
        
        # Запуск миграции
        print("\n4. ЗАПУСК МИГРАЦИИ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan migrate --force 2>&1")
        print(output)
        
        # Проверка структуры
        print("\n5. СТРУКТУРА ТАБЛИЦЫ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && sqlite3 database/database.sqlite '.schema personal_access_tokens' 2>&1")
        print(output)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

