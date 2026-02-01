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

print("=== Исправление таблицы jobs через SQL ===\n")

# Создаем SQL файл
sql_content = """
DROP TABLE IF EXISTS jobs;
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    queue VARCHAR(255) NOT NULL,
    payload TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    reserved_at INTEGER NULL,
    available_at INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS jobs_queue_index ON jobs(queue);
"""

# Сохраняем SQL файл
sftp = ssh.open_sftp()
with sftp.file("/tmp/fix_jobs.sql", 'w') as f:
    f.write(sql_content)
sftp.close()

# Выполняем SQL через sqlite3
print("[1] Выполнение SQL...")
db_path = "/root/shannon/backend-laravel/database/database.sqlite"
stdin, stdout, stderr = ssh.exec_command(f"sqlite3 {db_path} < /tmp/fix_jobs.sql 2>&1")
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
print("\n[2] Проверка структуры:")
stdin, stdout, stderr = ssh.exec_command(f"sqlite3 {db_path} \"PRAGMA table_info(jobs);\"")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Тестируем добавление job
print("\n[3] Тест добавления job...")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"DB::table('jobs')->insert(['queue' => 'default', 'payload' => json_encode(['test' => true]), 'attempts' => 0, 'available_at' => time(), 'created_at' => time()]); echo 'Job ID: ' . DB::getPdo()->lastInsertId();\" 2>&1 | tail -5")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
    if 'Job ID:' in output:
        print("✓ Job успешно добавлен с auto-increment ID")
except:
    pass

ssh.close()


