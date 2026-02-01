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

print("=== Отладка очереди и авторизации ===\n")

# Проверяем что Laravel использует правильную конфигурацию
print("[1] Проверка конфигурации очереди в Laravel:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo config('queue.default');\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"Очередь по умолчанию: {output}")
    if 'sync' in output.lower():
        print("✗ Все еще используется sync - нужно перезапустить Laravel")
except:
    pass

# Проверяем .env
print("\n[2] Проверка .env:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && cat .env | grep -E 'QUEUE_CONNECTION|APP_ENV'")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Очищаем кэш конфигурации
print("\n[3] Очистка кэша конфигурации...")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && php artisan config:clear && php artisan cache:clear")
stdout.channel.settimeout(5)
stdout.read()

# Перезапускаем Laravel
print("[4] Перезапуск Laravel...")
stdin, stdout, stderr = ssh.exec_command("systemctl restart shannon-laravel.service")
stdout.channel.settimeout(3)
stdout.read()

import time
time.sleep(3)

# Проверяем конфигурацию снова
print("\n[5] Проверка конфигурации после перезапуска:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo config('queue.default');\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"Очередь по умолчанию: {output}")
except:
    pass

# Проверяем что API работает
print("\n[6] Тест API:")
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

ssh.close()


