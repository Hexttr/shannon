#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import paramiko
import re

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("72.56.79.153", port=22, username="root", password="m8J@2_6whwza6U", timeout=10)

print("=== Отладка отображения логов ===\n")

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

# Получаем список пентестов
print("\n[2] Получение списка пентестов...")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests -H 'Authorization: Bearer {token}' -H 'Accept: application/json'")
stdout.channel.settimeout(5)
pentests_output = stdout.read().decode('utf-8', errors='ignore')

# Находим все пентесты
pentest_ids = re.findall(r'"id":"([^"]+)"', pentests_output)
print(f"Найдено пентестов: {len(pentest_ids)}")

# Проверяем логи для каждого пентеста
for pentest_id in pentest_ids[:3]:  # Проверяем первые 3
    print(f"\n[3] Проверка логов пентеста {pentest_id[:8]}...")
    stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests/{pentest_id}/logs -H 'Authorization: Bearer {token}' -H 'Accept: application/json'")
    stdout.channel.settimeout(5)
    logs_output = stdout.read().decode('utf-8', errors='ignore')
    
    if '"data":[]' in logs_output:
        print("  Логи пусты")
    elif '"data":[' in logs_output:
        log_count = len(re.findall(r'"id":"[^"]+"', logs_output))
        print(f"  Логов: {log_count}")
        if log_count > 0:
            # Показываем первый лог
            first_log_match = re.search(r'"message":"([^"]+)"', logs_output)
            if first_log_match:
                print(f"  Первый лог: {first_log_match.group(1)[:50]}...")
    else:
        print(f"  Ответ: {logs_output[:200]}")

# Проверяем логи напрямую в БД
print("\n[4] Проверка логов в БД:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo json_encode(DB::table('logs')->select('pentest_id', 'level', 'message')->limit(5)->get());\" 2>&1 | tail -10")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

ssh.close()

