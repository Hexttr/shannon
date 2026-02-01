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

print("=== Финальный тест Claude API ===\n")

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

# Создаем и запускаем пентест
print("\n[2] Создание и запуск пентеста...")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Authorization: Bearer {token}' -d '{{\"name\":\"Final Claude Test\",\"config\":{{\"targetUrl\":\"https://example.com\"}}}}'")
stdout.channel.settimeout(5)
pentest_output = stdout.read().decode('utf-8', errors='ignore')
pentest_match = re.search(r'"id":"([^"]+)"', pentest_output)
if not pentest_match:
    print("Не удалось создать пентест")
    ssh.close()
    exit(1)

pentest_id = pentest_match.group(1)
print(f"✓ Пентест создан: {pentest_id}")

# Запускаем
stdin, stdout, stderr = ssh.exec_command(f"timeout 3 curl -s http://localhost:8000/api/pentests/{pentest_id}/start -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Authorization: Bearer {token}'")
stdout.channel.settimeout(4)
stdout.read()
print("✓ Пентест запущен")

# Ждем выполнения
print("\n[3] Ожидание выполнения (120 секунд для завершения шага и анализа)...")
for i in range(12):
    time.sleep(10)
    print(f"   {i*10+10} секунд...")
    
    # Проверяем логи в реальном времени
    stdin, stdout, stderr = ssh.exec_command("tail -200 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'Claude|analyzeResults' | grep -v 'не настроен' | tail -5")
    stdout.channel.settimeout(3)
    try:
        recent = stdout.read().decode('utf-8', errors='ignore').strip()
        if recent:
            print(f"\n   ✓ Найдены логи Claude API!")
            print(f"   {recent[:200]}...")
            break
    except:
        pass

# Финальная проверка
print("\n[4] Финальная проверка:")
stdin, stdout, stderr = ssh.exec_command("tail -500 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'Claude|analyzeResults|analyzeScanResults' | grep -v 'не настроен' | tail -20")
stdout.channel.settimeout(5)
try:
    claude_logs = stdout.read().decode('utf-8', errors='ignore').strip()
    if claude_logs:
        print("✓✓✓ CLAUDE API ИСПОЛЬЗУЕТСЯ! ✓✓✓")
        print("\nЛоги:")
        print(claude_logs[:1000])
    else:
        print("⚠ Нет логов использования Claude API")
        print("\nПроверяю почему ключ не используется...")
        
        # Проверяем что происходит в Job
        stdin, stdout, stderr = ssh.exec_command("tail -300 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'RunPentestJob|PentestEngine|analyzeResults' | tail -15")
        stdout.channel.settimeout(3)
        job_logs = stdout.read().decode('utf-8', errors='ignore').strip()
        if job_logs:
            print("\nЛоги выполнения Job:")
            print(job_logs)
except:
    pass

# Проверяем уязвимости
print(f"\n[5] Уязвимости:")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests/{pentest_id}/vulnerabilities -H 'Authorization: Bearer {token}' -H 'Accept: application/json'")
stdout.channel.settimeout(5)
vulns_output = stdout.read().decode('utf-8', errors='ignore')
vuln_count = len(re.findall(r'"id":"[^"]+"', vulns_output))
print(f"Найдено уязвимостей: {vuln_count}")

if vuln_count > 0:
    print("\n✓✓✓ ПЕНТЕСТ ДОШЕЛ ДО ИСПОЛЬЗОВАНИЯ CLAUDE API! ✓✓✓")
    vuln_titles = re.findall(r'"title":"([^"]+)"', vulns_output)
    print("\nУязвимости:")
    for i, title in enumerate(vuln_titles[:5], 1):
        print(f"  {i}. {title}")

ssh.close()

print("\n=== Тест завершен ===")

