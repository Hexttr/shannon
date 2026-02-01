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

print("=== Исправление таблицы failed_jobs ===\n")

# Загружаем исправленную миграцию
print("[1] Загрузка исправленной миграции...")
sftp = ssh.open_sftp()
with open("backend-laravel/database/migrations/2024_01_01_000007_create_jobs_table.php", 'r', encoding='utf-8') as f:
    content = f.read()
with sftp.file("/root/shannon/backend-laravel/database/migrations/2024_01_01_000007_create_jobs_table.php", 'w') as rf:
    rf.write(content.encode('utf-8'))
sftp.close()
print("✓ Миграция загружена")

# Пересоздаем таблицу failed_jobs через SQL
print("\n[2] Пересоздание таблицы failed_jobs...")
db_path = "/root/shannon/backend-laravel/database/database.sqlite"
sql = """
DROP TABLE IF EXISTS failed_jobs;
CREATE TABLE failed_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    uuid VARCHAR(255) NOT NULL UNIQUE,
    connection TEXT NOT NULL,
    queue TEXT NOT NULL,
    payload TEXT NOT NULL,
    exception TEXT NOT NULL,
    failed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS failed_jobs_uuid_unique ON failed_jobs(uuid);
"""

# Сохраняем SQL файл
sftp = ssh.open_sftp()
with sftp.file("/tmp/fix_failed_jobs.sql", 'w') as f:
    f.write(sql)
sftp.close()

# Выполняем SQL
stdin, stdout, stderr = ssh.exec_command(f"sqlite3 {db_path} < /tmp/fix_failed_jobs.sql 2>&1")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    if output.strip():
        print(f"Ошибка: {output}")
    else:
        print("✓ Таблица пересоздана")
except:
    pass

# Проверяем структуру
print("\n[3] Проверка структуры:")
stdin, stdout, stderr = ssh.exec_command(f"sqlite3 {db_path} \"PRAGMA table_info(failed_jobs);\"")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

ssh.close()

