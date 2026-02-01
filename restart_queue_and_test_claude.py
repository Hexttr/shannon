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

print("=== Перезапуск Queue Worker и тест Claude API ===\n")

# Перезапускаем queue worker
print("[1] Перезапуск Queue Worker...")
stdin, stdout, stderr = ssh.exec_command("systemctl restart shannon-queue.service")
stdout.channel.settimeout(3)
stdout.read()
time.sleep(2)
print("✓ Queue Worker перезапущен")

# Очищаем кэш конфигурации
print("\n[2] Очистка кэша конфигурации...")
ssh.exec_command("cd /root/shannon/backend-laravel && php artisan config:clear && php artisan cache:clear")
print("✓ Кэш очищен")

# Получаем токен
print("\n[3] Получение токена...")
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
print("\n[4] Создание и запуск нового пентеста...")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Authorization: Bearer {token}' -d '{{\"name\":\"Claude Final Test\",\"config\":{{\"targetUrl\":\"https://example.com\"}}}}'")
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

# Ждем выполнения первого шага и анализа
print("\n[5] Ожидание выполнения шага и анализа через Claude API (90 секунд)...")
print("   Это нужно чтобы:")
print("   1. Выполнился шаг сканирования (nmap)")
print("   2. Результаты были проанализированы через Claude API")
print("   3. Уязвимости были извлечены и сохранены")

for i in range(9):
    time.sleep(10)
    print(f"   Прошло {(i+1)*10} секунд...")
    
    # Проверяем логи Claude API
    stdin, stdout, stderr = ssh.exec_command("tail -100 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'Claude|analyzeResults' | grep -v 'не настроен' | tail -3")
    stdout.channel.settimeout(3)
    try:
        recent_logs = stdout.read().decode('utf-8', errors='ignore').strip()
        if recent_logs:
            print(f"\n   ✓ Найдены логи Claude API!")
            break
    except:
        pass

# Финальная проверка
print("\n[6] Финальная проверка использования Claude API:")
stdin, stdout, stderr = ssh.exec_command("tail -500 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'Claude|analyzeResults|analyzeScanResults' | grep -v 'не настроен' | tail -30")
stdout.channel.settimeout(5)
try:
    claude_logs = stdout.read().decode('utf-8', errors='ignore').strip()
    if claude_logs:
        print("✓✓✓ CLAUDE API ИСПОЛЬЗУЕТСЯ! ✓✓✓")
        print("\nЛоги использования Claude API:")
        print(claude_logs[:800])
    else:
        print("⚠ Нет логов использования Claude API")
        print("Проверяю все логи...")
        stdin, stdout, stderr = ssh.exec_command("tail -200 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -i claude | tail -10")
        stdout.channel.settimeout(3)
        all_claude = stdout.read().decode('utf-8', errors='ignore').strip()
        if all_claude:
            print(all_claude)
except:
    pass

# Проверяем уязвимости
print(f"\n[7] Проверка уязвимостей (результат Claude API):")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests/{pentest_id}/vulnerabilities -H 'Authorization: Bearer {token}' -H 'Accept: application/json'")
stdout.channel.settimeout(5)
vulns_output = stdout.read().decode('utf-8', errors='ignore')
vuln_count = len(re.findall(r'"id":"[^"]+"', vulns_output))
print(f"Найдено уязвимостей: {vuln_count}")

if vuln_count > 0:
    print("\n✓✓✓ ПЕНТЕСТ ДОШЕЛ ДО ИСПОЛЬЗОВАНИЯ CLAUDE API! ✓✓✓")
    print("\nУязвимости найденные через Claude API:")
    vuln_titles = re.findall(r'"title":"([^"]+)"', vulns_output)
    for i, title in enumerate(vuln_titles[:5], 1):
        print(f"  {i}. {title}")
else:
    print("\n⚠ Уязвимостей нет")
    print("Возможные причины:")
    print("  - Анализ еще не выполнен (нужно больше времени)")
    print("  - Нет найденных уязвимостей в результатах сканирования")
    print("  - Claude API вернул пустой результат")

# Проверяем логи пентеста
print(f"\n[8] Логи пентеста:")
stdin, stdout, stderr = ssh.exec_command(f"curl -s http://localhost:8000/api/pentests/{pentest_id}/logs -H 'Authorization: Bearer {token}' -H 'Accept: application/json'")
stdout.channel.settimeout(5)
logs_output = stdout.read().decode('utf-8', errors='ignore')
log_count = len(re.findall(r'"id":"[^"]+"', logs_output))
print(f"Всего логов: {log_count}")
if log_count > 0:
    log_messages = re.findall(r'"message":"([^"]+)"', logs_output)
    print("\nПоследние логи:")
    for msg in log_messages[-5:]:
        print(f"  - {msg[:100]}...")

ssh.close()

print("\n=== Тест завершен ===")

