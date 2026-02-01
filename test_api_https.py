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

print("=== Тест API через HTTPS ===\n")

# Тест API через HTTPS (как делает браузер)
print("[1] Тест /api/auth/login через HTTPS:")
stdin, stdout, stderr = ssh.exec_command("curl -k -s -X POST https://localhost/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' -w '\\nHTTP_CODE:%{http_code}'")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if 'HTTP_CODE:200' in output or 'token' in output:
        print("✓ API работает через HTTPS")
        print(output[:300])
    else:
        print(f"✗ Проблема: {output[-200:]}")
except Exception as e:
    print(f"Ошибка: {e}")

# Проверка Nginx конфигурации
print("\n[2] Проверка Nginx конфигурации для /api:")
stdin, stdout, stderr = ssh.exec_command("grep -A 5 'location /api' /etc/nginx/sites-available/shannon")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output)
except:
    pass

# Проверка что Laravel слушает на порту 8000
print("\n[3] Проверка Laravel на порту 8000:")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' | head -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if 'token' in output:
        print("✓ Laravel работает на порту 8000")
    else:
        print(f"Ответ: {output[:200]}")
except:
    print("Таймаут")

ssh.close()
print("\n=== Тест завершен ===")


