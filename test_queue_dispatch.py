#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import paramiko
import re
import time

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("72.56.79.153", port=22, username="root", password="m8J@2_6whwza6U", timeout=10)

print("=== Тест dispatch в очередь ===\n")

# Получаем токен
print("[1] Получение токена...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}'")
stdout.channel.settimeout(5)
login_output = stdout.read().decode('utf-8', errors='ignore')
token_match = re.search(r'"token":"([^"]+)"', login_output)
if not token_match:
    print("Не удалось получить токен")
    ssh.close()
    exit(1)

token = token_match.group(1)

# Создаем пентест
print("\n[2] Создание пентеста...")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Authorization: Bearer {token}' -d '{{\"name\":\"Queue Test 2\",\"config\":{{\"targetUrl\":\"https://example.com\"}}}}'")
stdout.channel.settimeout(5)
pentest_output = stdout.read().decode('utf-8', errors='ignore')
pentest_match = re.search(r'"id":"([^"]+)"', pentest_output)
if not pentest_match:
    print(f"Не удалось создать пентест")
    ssh.close()
    exit(1)

pentest_id = pentest_match.group(1)
print(f"✓ Пентест создан: {pentest_id}")

# Проверяем очередь ДО запуска
print("\n[3] Очередь ДО запуска:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 2 php artisan tinker --execute=\"echo DB::table('jobs')->count();\" 2>&1 | tail -3")
stdout.channel.settimeout(3)
try:
    before_count = stdout.read().decode('utf-8', errors='ignore').strip().split('\n')[-1]
    print(f"Заданий: {before_count}")
except:
    pass

# Запускаем пентест
print(f"\n[4] Запуск пентеста...")
stdin, stdout, stderr = ssh.exec_command(f"timeout 2 curl -s http://localhost:8000/api/pentests/{pentest_id}/start -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Authorization: Bearer {token}'")
stdout.channel.settimeout(3)
start_output = stdout.read().decode('utf-8', errors='ignore')

# Сразу проверяем очередь ПОСЛЕ запуска
print("\n[5] Очередь ПОСЛЕ запуска (сразу):")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 2 php artisan tinker --execute=\"echo DB::table('jobs')->count();\" 2>&1 | tail -3")
stdout.channel.settimeout(3)
try:
    after_count = stdout.read().decode('utf-8', errors='ignore').strip().split('\n')[-1]
    print(f"Заданий: {after_count}")
    if int(after_count) > int(before_count):
        print("✓ Job добавлен в очередь")
    else:
        print("✗ Job НЕ добавлен в очередь (возможно sync)")
except:
    pass

# Ждем немного
time.sleep(2)

# Проверяем очередь снова
print("\n[6] Очередь через 2 секунды:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 2 php artisan tinker --execute=\"echo DB::table('jobs')->count();\" 2>&1 | tail -3")
stdout.channel.settimeout(3)
try:
    final_count = stdout.read().decode('utf-8', errors='ignore').strip().split('\n')[-1]
    print(f"Заданий: {final_count}")
    if int(final_count) == 0:
        print("✓ Job обработан")
except:
    pass

# Проверяем логи
print(f"\n[7] Проверка логов пентеста:")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests/{pentest_id}/logs -H 'Authorization: Bearer {token}' -H 'Accept: application/json'")
stdout.channel.settimeout(5)
logs_output = stdout.read().decode('utf-8', errors='ignore')
log_count = len(re.findall(r'"id":"[^"]+"', logs_output))
print(f"Логов: {log_count}")

ssh.close()


