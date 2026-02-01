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

print("=== Финальная проверка ===\n")

# Проверка файлов
print("[1] Проверка ключевых файлов:")
files = [
    "/root/shannon/backend-laravel/app/Http/Middleware/Authenticate.php",
    "/root/shannon/backend-laravel/app/Services/ClaudeApiService.php",
    "/root/shannon/template/src/services/api.ts",
    "/root/shannon/template/dist/index.html"
]

for file in files:
    stdin, stdout, stderr = ssh.exec_command(f"test -f {file} && echo 'EXISTS' || echo 'NOT_FOUND'")
    stdout.channel.settimeout(2)
    try:
        status = stdout.read().decode('utf-8').strip()
        print(f"  {os.path.basename(file)}: {status}")
    except:
        pass

# Проверка API
print("\n[2] Тест API:")
stdin, stdout, stderr = ssh.exec_command("timeout 3 curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' | head -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if 'token' in output:
        print("  ✓ API работает")
    else:
        print(f"  Ответ: {output[:100]}")
except:
    print("  Таймаут")

# Проверка статуса сервисов
print("\n[3] Статус сервисов:")
stdin, stdout, stderr = ssh.exec_command("systemctl is-active shannon-laravel.service nginx.service")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8').strip()
    print(f"  {output}")
except:
    pass

ssh.close()
print("\n=== Проверка завершена ===")
print("\nПопробуйте войти в систему:")
print("  URL: https://72.56.79.153")
print("  Логин: admin")
print("  Пароль: admin")

