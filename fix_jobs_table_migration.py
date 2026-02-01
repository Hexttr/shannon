#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import paramiko

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("72.56.79.153", port=22, username="root", password="m8J@2_6whwza6U", timeout=10)

print("=== Исправление таблицы jobs ===\n")

# Загружаем исправленную миграцию
print("[1] Загрузка исправленной миграции...")
sftp = ssh.open_sftp()
with open("backend-laravel/database/migrations/2024_01_01_000007_create_jobs_table.php", 'r', encoding='utf-8') as f:
    content = f.read()
with sftp.file("/root/shannon/backend-laravel/database/migrations/2024_01_01_000007_create_jobs_table.php", 'w') as rf:
    rf.write(content)
sftp.close()
print("OK")

# Пересоздаем таблицу jobs
print("\n[2] Пересоздание таблицы jobs...")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && php artisan migrate:fresh --path=database/migrations/2024_01_01_000007_create_jobs_table.php --force 2>&1 | tail -10")
stdout.channel.settimeout(10)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Или просто пересоздаем таблицу вручную
print("\n[3] Пересоздание таблицы jobs вручную...")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && php artisan tinker --execute=\"DB::statement('DROP TABLE IF EXISTS jobs'); DB::statement('CREATE TABLE jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, queue VARCHAR(255) NOT NULL, payload TEXT NOT NULL, attempts INTEGER NOT NULL, reserved_at INTEGER NULL, available_at INTEGER NOT NULL, created_at INTEGER NOT NULL)'); echo 'OK';\" 2>&1 | tail -5")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Проверяем структуру
print("\n[4] Проверка структуры таблицы:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo json_encode(DB::select('PRAGMA table_info(jobs)'));\" 2>&1 | tail -10")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

ssh.close()


