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

print("=== Тест интеграции Claude API ===\n")

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

# Очищаем старые логи Claude API для чистого теста
print("\n[2] Очистка старых логов...")
ssh.exec_command("echo '' > /tmp/claude_test_logs.txt")

# Создаем и запускаем пентест
print("\n[3] Создание и запуск пентеста...")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Authorization: Bearer {token}' -d '{{\"name\":\"Claude Integration Test\",\"config\":{{\"targetUrl\":\"https://example.com\"}}}}'")
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

# Ждем выполнения шагов (nmap обычно быстрый)
print("\n[4] Ожидание выполнения шагов сканирования (60 секунд)...")
print("   (Это нужно чтобы дождаться завершения шага и анализа через Claude API)")
for i in range(6):
    time.sleep(10)
    print(f"   Прошло {(i+1)*10} секунд...")
    
    # Проверяем логи в реальном времени
    stdin, stdout, stderr = ssh.exec_command("tail -50 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'Claude|analyzeResults|analyzeScanResults' | tail -5")
    stdout.channel.settimeout(3)
    try:
        recent_logs = stdout.read().decode('utf-8', errors='ignore').strip()
        if recent_logs and 'Claude API key не настроен' not in recent_logs:
            print(f"\n✓ Найдены логи Claude API!")
            print(recent_logs[:400])
            break
    except:
        pass

# Финальная проверка использования Claude API
print("\n[5] Финальная проверка использования Claude API:")
stdin, stdout, stderr = ssh.exec_command("tail -300 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'Claude|analyzeResults|analyzeScanResults' | grep -v 'не настроен' | tail -20")
stdout.channel.settimeout(5)
try:
    claude_logs = stdout.read().decode('utf-8', errors='ignore').strip()
    if claude_logs:
        print("✓ Claude API используется!")
        print("\nЛоги использования Claude API:")
        print(claude_logs)
    else:
        print("⚠ Нет логов использования Claude API")
        print("Проверяю все логи Claude...")
        stdin, stdout, stderr = ssh.exec_command("tail -100 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -i claude | tail -10")
        stdout.channel.settimeout(3)
        all_claude = stdout.read().decode('utf-8', errors='ignore').strip()
        if all_claude:
            print(all_claude)
except:
    pass

# Проверяем уязвимости
print(f"\n[6] Проверка уязвимостей (результат анализа Claude API):")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests/{pentest_id}/vulnerabilities -H 'Authorization: Bearer {token}' -H 'Accept: application/json'")
stdout.channel.settimeout(5)
vulns_output = stdout.read().decode('utf-8', errors='ignore')
vuln_count = len(re.findall(r'"id":"[^"]+"', vulns_output))
print(f"Найдено уязвимостей: {vuln_count}")

if vuln_count > 0:
    print("✓✓✓ ПЕНТЕСТ ДОШЕЛ ДО ИСПОЛЬЗОВАНИЯ CLAUDE API! ✓✓✓")
    print("\nУязвимости найденные через Claude API:")
    # Показываем первые 3 уязвимости
    vuln_titles = re.findall(r'"title":"([^"]+)"', vulns_output)
    for i, title in enumerate(vuln_titles[:3], 1):
        print(f"  {i}. {title}")
else:
    print("⚠ Уязвимостей нет (возможно:")
    print("   - Анализ еще не выполнен")
    print("   - Нет найденных уязвимостей в результатах сканирования")
    print("   - Claude API вернул пустой результат)")

# Проверяем логи пентеста
print(f"\n[7] Логи пентеста:")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests/{pentest_id}/logs -H 'Authorization: Bearer {token}' -H 'Accept: application/json'")
stdout.channel.settimeout(5)
logs_output = stdout.read().decode('utf-8', errors='ignore')
log_count = len(re.findall(r'"id":"[^"]+"', logs_output))
print(f"Всего логов: {log_count}")

# Проверяем статус пентеста
print(f"\n[8] Статус пентеста:")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests/{pentest_id}/status -H 'Authorization: Bearer {token}' -H 'Accept: application/json'")
stdout.channel.settimeout(5)
status_output = stdout.read().decode('utf-8', errors='ignore')
status_match = re.search(r'"status":"([^"]+)"', status_output)
if status_match:
    print(f"Статус: {status_match.group(1)}")

ssh.close()

print("\n=== Тест завершен ===")


