#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновление миграции на сервере напрямую
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
    sftp = ssh.open_sftp()
    
    try:
        # 1. Обновление репозитория
        print("1. ОБНОВЛЕНИЕ РЕПОЗИТОРИЯ:")
        ssh_exec(ssh, "cd /root/shannon && git pull")
        
        # 2. Копирование правильного файла миграции
        print("\n2. КОПИРОВАНИЕ ФАЙЛА МИГРАЦИИ:")
        local_file = "backend-laravel/database/migrations/2024_01_01_000006_create_personal_access_tokens_table.php"
        remote_file = f"{BACKEND_DIR}/database/migrations/2024_01_01_000006_create_personal_access_tokens_table.php"
        
        with open(local_file, 'rb') as f:
            sftp.putfo(f, remote_file)
        print("  [OK] Файл скопирован")
        
        # 3. Удаление записи и таблицы
        print("\n3. УДАЛЕНИЕ И ПЕРЕСОЗДАНИЕ:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && sqlite3 database/database.sqlite \"DELETE FROM migrations WHERE migration = '2024_01_01_000006_create_personal_access_tokens_table';\" 2>&1")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && sqlite3 database/database.sqlite 'DROP TABLE IF EXISTS personal_access_tokens;' 2>&1")
        
        # 4. Запуск миграции
        print("\n4. ЗАПУСК МИГРАЦИИ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan migrate --force 2>&1")
        print(output)
        
        # 5. Проверка структуры
        print("\n5. СТРУКТУРА ТАБЛИЦЫ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && sqlite3 database/database.sqlite '.schema personal_access_tokens' 2>&1")
        print(output)
        
        if "INTEGER" in output or "integer" in output.lower():
            print("  [OK] Таблица создана с INTEGER id")
        else:
            print("  [WARNING] Все еще varchar")
        
        # 6. Очистка и перезапуск
        print("\n6. ОЧИСТКА И ПЕРЕЗАПУСК:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan optimize:clear 2>&1")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service")
        time.sleep(4)
        
        # 7. Тест API
        print("\n7. ТЕСТ API:")
        success, output, error = ssh_exec(ssh, "curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}'")
        print(f"Ответ: {output[:600]}")
        
        if '"token"' in output and '"user"' in output:
            print("\n✅ [SUCCESS] API РАБОТАЕТ!")
        elif "validation" in output.lower():
            print("\n✅ [SUCCESS] API отвечает")
        else:
            print("\n❌ [ERROR] Проверьте логи")
            success, output, error = ssh_exec(ssh, f"tail -20 {BACKEND_DIR}/storage/logs/laravel.log")
            print(output[-500:])
        
    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    main()

