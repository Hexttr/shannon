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

print("=== Тест Claude API с правильным форматом ===\n")

# Проверяем что ключ правильно читается (без пробелов)
print("[1] Проверка формата ключа в .env:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && grep '^CLAUDE_API_KEY=' .env | sed 's/.*=//' | wc -c")
stdout.channel.settimeout(3)
try:
    key_length = int(stdout.read().decode('utf-8').strip())
    print(f"Длина ключа: {key_length} символов (включая \\n)")
    if key_length == 109:  # 108 символов + \n
        print("✓ Длина ключа правильная")
    else:
        print(f"⚠ Неправильная длина (ожидается 108, получено {key_length-1})")
except:
    pass

# Проверяем что ключ загружается без пробелов
print("\n[2] Проверка загрузки ключа через Laravel:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 5 php artisan tinker --execute=\"\\$key = trim(config('services.claude.api_key')); echo 'LENGTH: ' . strlen(\\$key) . ' FIRST_CHARS: ' . substr(\\$key, 0, 20);\" 2>&1 | tail -5")
stdout.channel.settimeout(6)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output)
except:
    pass

# Создаем и запускаем пентест
print("\n[3] Создание и запуск пентеста...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}'")
stdout.channel.settimeout(5)
login_output = stdout.read().decode('utf-8', errors='ignore')
token_match = re.search(r'"token":"([^"]+)"', login_output)
if not token_match:
    print("Не удалось получить токен")
    ssh.close()
    exit(1)

token = token_match.group(1)

stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Authorization: Bearer {token}' -d '{{\"name\":\"Claude Format Test\",\"config\":{{\"targetUrl\":\"https://example.com\"}}}}'")
stdout.channel.settimeout(5)
pentest_output = stdout.read().decode('utf-8', errors='ignore')
pentest_match = re.search(r'"id":"([^"]+)"', pentest_output)
if not pentest_match:
    print("Не удалось создать пентест")
    ssh.close()
    exit(1)

pentest_id = pentest_match.group(1)
print(f"✓ Пентест создан: {pentest_id}")

stdin, stdout, stderr = ssh.exec_command(f"timeout 3 curl -s http://localhost:8000/api/pentests/{pentest_id}/start -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Authorization: Bearer {token}'")
stdout.channel.settimeout(4)
stdout.read()
print("✓ Пентест запущен")

# Ждем выполнения
print("\n[4] Ожидание выполнения (60 секунд)...")
for i in range(6):
    time.sleep(10)
    print(f"   {i*10+10} секунд...")
    
    # Проверяем логи
    stdin, stdout, stderr = ssh.exec_command("tail -100 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'Claude API|analyzeResults' | tail -5")
    stdout.channel.settimeout(3)
    try:
        recent = stdout.read().decode('utf-8', errors='ignore').strip()
        if recent and 'invalid x-api-key' not in recent and 'не настроен' not in recent:
            print(f"\n   ✓ Найдены успешные логи Claude API!")
            print(f"   {recent[:300]}...")
            break
        elif recent and 'invalid x-api-key' in recent:
            print(f"\n   ⚠ Все еще ошибка аутентификации")
            print(f"   {recent[:300]}...")
    except:
        pass

# Финальная проверка
print("\n[5] Финальная проверка:")
stdin, stdout, stderr = ssh.exec_command("tail -200 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'Claude API|analyzeResults' | tail -10")
stdout.channel.settimeout(5)
try:
    logs = stdout.read().decode('utf-8', errors='ignore').strip()
    if logs:
        print("Логи Claude API:")
        print(logs[:800])
        if 'invalid x-api-key' in logs:
            print("\n⚠ Ошибка: invalid x-api-key")
            print("Возможные причины:")
            print("  1. Ключ неправильный или истек")
            print("  2. Ключ содержит лишние пробелы или символы")
            print("  3. Неправильный формат заголовка")
except:
    pass

ssh.close()

