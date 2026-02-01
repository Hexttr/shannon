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

print("=== Финальные исправления и тест ===\n")

# Останавливаем зависшие процессы пентеста
print("[1] Остановка зависших процессов пентеста:")
stdin, stdout, stderr = ssh.exec_command("pkill -f 'nmap|nikto|nuclei|dirb|sqlmap' || echo 'Нет процессов'")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Проверяем статус queue worker
print("\n[2] Статус queue worker:")
stdin, stdout, stderr = ssh.exec_command("systemctl is-active shannon-queue.service")
stdout.channel.settimeout(3)
try:
    status = stdout.read().decode('utf-8').strip()
    print(f"Статус: {status}")
except:
    pass

# Перезапускаем Laravel для применения изменений
print("\n[3] Перезапуск Laravel...")
stdin, stdout, stderr = ssh.exec_command("systemctl restart shannon-laravel.service")
stdout.channel.settimeout(3)
stdout.read()

import time
time.sleep(3)

# Тест API
print("\n[4] Тест API после перезапуска:")
stdin, stdout, stderr = ssh.exec_command("timeout 5 curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' | head -3")
stdout.channel.settimeout(6)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if 'token' in output:
        print("✓ API работает")
    else:
        print(f"Ответ: {output[:200]}")
except:
    print("Таймаут")

# Проверяем процессы
print("\n[5] Активные процессы:")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'php.*artisan|queue:work' | grep -v grep")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

ssh.close()
print("\n=== Готово ===")


