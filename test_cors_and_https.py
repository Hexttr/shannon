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

print("=== Тест CORS и HTTPS ===\n")

# Тест через HTTPS с CORS заголовками (как делает браузер)
print("[1] Тест через HTTPS с CORS:")
stdin, stdout, stderr = ssh.exec_command("timeout 5 curl -k -s -X POST https://localhost/api/auth/login -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'Origin: https://72.56.79.153' -d '{\"username\":\"admin\",\"password\":\"admin\"}' -v 2>&1 | grep -E 'HTTP|Access-Control|token' | head -10")
stdout.channel.settimeout(6)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
    if 'token' in output or '200' in output:
        print("\n✓ API работает через HTTPS")
except Exception as e:
    print(f"Ошибка: {e}")

# Проверка CORS конфигурации
print("\n[2] Проверка CORS конфигурации:")
stdin, stdout, stderr = ssh.exec_command("grep -A 10 'allowed_origins' /root/shannon/backend-laravel/config/cors.php")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Проверка .env для CORS
print("\n[3] Проверка FRONTEND_URL в .env:")
stdin, stdout, stderr = ssh.exec_command("grep FRONTEND_URL /root/shannon/backend-laravel/.env || echo 'Не найдено'")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output)
except:
    pass

ssh.close()
print("\n=== Тест завершен ===")

