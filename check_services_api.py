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

print("=== Проверка API сервисов ===\n")

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

# Проверяем API сервисов
print("\n[2] Проверка API /api/services:")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/services -H 'Authorization: Bearer {token}' -H 'Accept: application/json'")
stdout.channel.settimeout(5)
services_output = stdout.read().decode('utf-8', errors='ignore')
print(f"Ответ API: {services_output[:500]}")

# Проверяем структуру ответа
if '"data":[' in services_output:
    service_count = len(re.findall(r'"id":"[^"]+"', services_output))
    print(f"\n✓ API возвращает данные")
    print(f"Найдено сервисов: {service_count}")
    if service_count == 0:
        print("⚠ Сервисов нет в базе данных")
    else:
        # Показываем первый сервис
        first_service = re.search(r'"id":"([^"]+)"[^}]*"name":"([^"]+)"[^}]*"url":"([^"]+)"', services_output)
        if first_service:
            print(f"\nПервый сервис:")
            print(f"  ID: {first_service.group(1)}")
            print(f"  Name: {first_service.group(2)}")
            print(f"  URL: {first_service.group(3)}")
elif 'error' in services_output.lower() or 'message' in services_output.lower():
    print(f"\n✗ Ошибка API:")
    print(services_output[:300])
else:
    print(f"\n⚠ Неожиданный формат ответа:")
    print(services_output[:300])

# Проверяем что сервисы есть в БД
print("\n[3] Проверка сервисов в БД:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo DB::table('services')->count();\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    db_count = stdout.read().decode('utf-8', errors='ignore').strip().split('\n')[-1]
    print(f"Сервисов в БД: {db_count}")
except:
    pass

ssh.close()

