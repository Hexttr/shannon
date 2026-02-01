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

print("=== Тест работы очереди ===\n")

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
print("✓ Токен получен")

# Создаем пентест
print("\n[2] Создание пентеста...")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Authorization: Bearer {token}' -d '{{\"name\":\"Queue Test\",\"config\":{{\"targetUrl\":\"https://example.com\"}}}}'")
stdout.channel.settimeout(5)
pentest_output = stdout.read().decode('utf-8', errors='ignore')
pentest_match = re.search(r'"id":"([^"]+)"', pentest_output)
if not pentest_match:
    print(f"Не удалось создать пентест: {pentest_output[:200]}")
    ssh.close()
    exit(1)

pentest_id = pentest_match.group(1)
print(f"✓ Пентест создан: {pentest_id}")

# Проверяем что job добавлен в очередь
print("\n[3] Проверка очереди:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo DB::table('jobs')->count();\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    job_count = re.search(r'(\d+)', output)
    if job_count:
        print(f"Заданий в очереди: {job_count.group(1)}")
except:
    pass

# Запускаем пентест
print(f"\n[4] Запуск пентеста {pentest_id}...")
stdin, stdout, stderr = ssh.exec_command(f"timeout 3 curl -s http://localhost:8000/api/pentests/{pentest_id}/start -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Authorization: Bearer {token}' -w '\\nHTTP_CODE:%{{http_code}}'")
stdout.channel.settimeout(5)
start_output = stdout.read().decode('utf-8', errors='ignore')

if 'HTTP_CODE:200' in start_output or 'message' in start_output.lower():
    print("✓ Пентест запущен")
    
    # Ждем немного
    import time
    time.sleep(2)
    
    # Проверяем что job обрабатывается
    print("\n[5] Проверка обработки job:")
    stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo DB::table('jobs')->count();\" 2>&1 | tail -3")
    stdout.channel.settimeout(5)
    try:
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        job_count = re.search(r'(\d+)', output)
        if job_count:
            print(f"Заданий в очереди после запуска: {job_count.group(1)}")
    except:
        pass
    
    # Проверяем что API все еще отвечает
    print("\n[6] Тест API после запуска пентеста:")
    stdin, stdout, stderr = ssh.exec_command("timeout 3 curl -s http://localhost:8000/api/auth/me -H 'Authorization: Bearer {token}' -H 'Accept: application/json' | head -3")
    stdout.channel.settimeout(4)
    try:
        output = stdout.read().decode('utf-8', errors='ignore')
        if 'username' in output or 'user' in output:
            print("✓ API отвечает (пользователь не выкинут)")
        else:
            print(f"Ответ: {output[:200]}")
    except:
        print("Таймаут - возможно API завис")
else:
    print(f"Ошибка запуска: {start_output[-300:]}")

ssh.close()


