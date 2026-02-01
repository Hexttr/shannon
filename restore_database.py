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

print("=== Восстановление базы данных ===\n")

# Запускаем все миграции
print("[1] Запуск миграций...")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && php artisan migrate --force 2>&1 | tail -20")
stdout.channel.settimeout(10)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Проверяем что таблицы созданы
print("\n[2] Проверка таблиц:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo implode(', ', DB::select('SELECT name FROM sqlite_master WHERE type=\"table\"'));\" 2>&1 | tail -5")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Перезапускаем Laravel
print("\n[3] Перезапуск Laravel...")
stdin, stdout, stderr = ssh.exec_command("systemctl restart shannon-laravel.service")
stdout.channel.settimeout(3)
stdout.read()

import time
time.sleep(3)

# Проверяем что Laravel работает
print("\n[4] Проверка Laravel:")
stdin, stdout, stderr = ssh.exec_command("timeout 3 curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' | head -3")
stdout.channel.settimeout(4)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    if 'token' in output:
        print("✓ Laravel работает")
    else:
        print(f"Ответ: {output[:200]}")
except:
    print("Таймаут")

ssh.close()


