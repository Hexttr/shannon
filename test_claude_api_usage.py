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

print("=== Тест использования Claude API ===\n")

# Проверяем что ключ настроен
print("[1] Проверка что ключ настроен:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo config('services.claude.api_key') ? 'KEY_SET' : 'KEY_NOT_SET';\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    key_status = output.split('\n')[-1] if '\n' in output else output
    if 'KEY_SET' in key_status:
        print("✓ Claude API key настроен")
    else:
        print(f"✗ Ключ не настроен: {key_status}")
except:
    pass

# Получаем токен
print("\n[2] Получение токена...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}'")
stdout.channel.settimeout(5)
login_output = stdout.read().decode('utf-8', errors='ignore')
token_match = re.search(r'"token":"([^"]+)"', login_output)
if not token_match:
    print("Не удалось получить токен")
    ssh.close()
    exit(1)

token = token_match.group(1)

# Создаем и запускаем пентест
print("\n[3] Создание и запуск пентеста...")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Authorization: Bearer {token}' -d '{{\"name\":\"Claude API Test\",\"config\":{{\"targetUrl\":\"https://example.com\"}}}}'")
stdout.channel.settimeout(5)
pentest_output = stdout.read().decode('utf-8', errors='ignore')
pentest_match = re.search(r'"id":"([^"]+)"', pentest_output)
if not pentest_match:
    print(f"Не удалось создать пентест")
    ssh.close()
    exit(1)

pentest_id = pentest_match.group(1)
print(f"✓ Пентест создан: {pentest_id}")

# Запускаем
stdin, stdout, stderr = ssh.exec_command(f"timeout 3 curl -s http://localhost:8000/api/pentests/{pentest_id}/start -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Authorization: Bearer {token}'")
stdout.channel.settimeout(4)
stdout.read()
print("✓ Пентест запущен")

# Ждем выполнения первого шага (nmap)
print("\n[4] Ожидание выполнения первого шага (30 секунд)...")
time.sleep(30)

# Проверяем логи Claude API
print("\n[5] Проверка использования Claude API:")
stdin, stdout, stderr = ssh.exec_command("tail -200 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'Claude|claude|analyzeResults|analyzeScanResults' | tail -20")
stdout.channel.settimeout(5)
try:
    claude_logs = stdout.read().decode('utf-8', errors='ignore').strip()
    if claude_logs:
        print("✓ Claude API используется!")
        print("\nЛоги Claude API:")
        print(claude_logs)
    else:
        print("⚠ Нет логов Claude API")
        print("Проверяю логи пентеста...")
        
        # Проверяем логи пентеста
        stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests/{pentest_id}/logs -H 'Authorization: Bearer {token}' -H 'Accept: application/json'")
        stdout.channel.settimeout(5)
        logs_output = stdout.read().decode('utf-8', errors='ignore')
        log_messages = re.findall(r'"message":"([^"]+)"', logs_output)
        print(f"\nЛогов пентеста: {len(log_messages)}")
        for msg in log_messages[-5:]:
            print(f"  - {msg[:80]}...")
except:
    pass

# Проверяем уязвимости
print(f"\n[6] Проверка уязвимостей:")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests/{pentest_id}/vulnerabilities -H 'Authorization: Bearer {token}' -H 'Accept: application/json'")
stdout.channel.settimeout(5)
vulns_output = stdout.read().decode('utf-8', errors='ignore')
vuln_count = len(re.findall(r'"id":"[^"]+"', vulns_output))
print(f"Найдено уязвимостей: {vuln_count}")
if vuln_count > 0:
    print("✓ Пентест дошел до анализа результатов через Claude API!")
    # Показываем первую уязвимость
    first_vuln = re.search(r'"title":"([^"]+)"', vulns_output)
    if first_vuln:
        print(f"Первая уязвимость: {first_vuln.group(1)}")
else:
    print("⚠ Уязвимостей нет (возможно анализ еще не выполнен или нет найденных уязвимостей)")

# Проверяем ошибки Claude API
print("\n[7] Проверка ошибок Claude API:")
stdin, stdout, stderr = ssh.exec_command("tail -100 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'Claude API error|Claude API exception|Claude API warning' | tail -10")
stdout.channel.settimeout(3)
try:
    errors = stdout.read().decode('utf-8', errors='ignore').strip()
    if errors:
        print("Ошибки Claude API:")
        print(errors)
    else:
        print("Нет ошибок Claude API")
except:
    pass

ssh.close()

print("\n=== Тест завершен ===")

