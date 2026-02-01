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

print("=== Пересоздание таблицы jobs правильно ===\n")

# Удаляем и пересоздаем таблицу с правильной структурой
print("[1] Пересоздание таблицы jobs...")
sql = """
DROP TABLE IF EXISTS jobs;
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    queue VARCHAR(255) NOT NULL,
    payload TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    reserved_at INTEGER NULL,
    available_at INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);
CREATE INDEX jobs_queue_index ON jobs(queue);
"""

stdin, stdout, stderr = ssh.exec_command(f"cd /root/shannon/backend-laravel && php artisan tinker --execute=\"{sql.replace(chr(10), ' ').replace(chr(13), ' ').replace('\"', '\\\"')}\" 2>&1 | tail -10")
stdout.channel.settimeout(10)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Проверяем структуру
print("\n[2] Проверка структуры:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo json_encode(DB::select('PRAGMA table_info(jobs)'));\" 2>&1 | tail -10")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Тестируем добавление job
print("\n[3] Тест добавления job в очередь...")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"DB::table('jobs')->insert(['queue' => 'default', 'payload' => 'test', 'attempts' => 0, 'available_at' => time(), 'created_at' => time()]); echo DB::table('jobs')->count();\" 2>&1 | tail -5")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

ssh.close()

