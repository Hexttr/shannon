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

print("=== Тест создания логов ===\n")

# Проверяем структуру таблицы logs
print("[1] Проверка структуры таблицы logs:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo json_encode(DB::select('PRAGMA table_info(logs)'));\" 2>&1 | tail -5")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Проверяем количество логов
print("\n[2] Количество логов в БД:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo DB::table('logs')->count();\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    log_count = output.split('\n')[-1] if '\n' in output else output
    print(f"Логов в БД: {log_count}")
except:
    pass

# Проверяем последние ошибки Laravel связанные с логами
print("\n[3] Ошибки создания логов:")
stdin, stdout, stderr = ssh.exec_command("tail -100 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'log|Log|addLog' | tail -10")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if output:
        print(output)
    else:
        print("Нет ошибок связанных с логами")
except:
    pass

ssh.close()

