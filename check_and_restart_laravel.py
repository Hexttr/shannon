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

print("=== Проверка и перезапуск Laravel ===\n")

# Проверка статуса
print("[1] Статус Laravel сервиса:")
stdin, stdout, stderr = ssh.exec_command("systemctl status shannon-laravel.service --no-pager | head -10")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Перезапуск Laravel
print("\n[2] Перезапуск Laravel:")
stdin, stdout, stderr = ssh.exec_command("systemctl restart shannon-laravel.service")
stdout.channel.settimeout(3)
try:
    stdout.read()
    print("✓ Сервис перезапущен")
except:
    pass

# Ждем немного
import time
time.sleep(2)

# Проверка что сервис запустился
print("\n[3] Проверка что сервис запущен:")
stdin, stdout, stderr = ssh.exec_command("systemctl is-active shannon-laravel.service")
stdout.channel.settimeout(3)
try:
    status = stdout.read().decode('utf-8').strip()
    print(f"Статус: {status}")
except:
    pass

# Тест API после перезапуска
print("\n[4] Тест API после перезапуска:")
stdin, stdout, stderr = ssh.exec_command("timeout 3 curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' || echo 'TIMEOUT'")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if 'token' in output:
        print("✓ API работает!")
        print(output[:200])
    elif 'TIMEOUT' in output:
        print("✗ API не отвечает (таймаут)")
    else:
        print(f"Ответ: {output[:200]}")
except:
    print("Ошибка чтения")

ssh.close()
print("\n=== Проверка завершена ===")

