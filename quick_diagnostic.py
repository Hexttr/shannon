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

print("=== Диагностика авторизации ===\n")

# 1. Ошибки Laravel
print("[1] Последние ошибки:")
stdin, stdout, stderr = ssh.exec_command("tail -20 /root/shannon/backend-laravel/storage/logs/laravel.log | grep ERROR | tail -5")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output if output else "Нет ошибок")
except:
    print("Таймаут чтения")

# 2. Тест API
print("\n[2] Тест API /auth/login:")
stdin, stdout, stderr = ssh.exec_command("curl -s -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}'")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output[:200])
except:
    print("Таймаут чтения")

# 3. Проверка файлов
print("\n[3] Проверка файлов:")
stdin, stdout, stderr = ssh.exec_command("test -f /root/shannon/backend-laravel/app/Http/Middleware/Authenticate.php && echo 'EXISTS' || echo 'NOT_FOUND'")
stdout.channel.settimeout(3)
try:
    print(f"Authenticate.php: {stdout.read().decode('utf-8').strip()}")
except:
    pass

stdin, stdout, stderr = ssh.exec_command("test -f /root/shannon/backend-laravel/app/Services/ClaudeApiService.php && echo 'EXISTS' || echo 'NOT_FOUND'")
stdout.channel.settimeout(3)
try:
    print(f"ClaudeApiService.php: {stdout.read().decode('utf-8').strip()}")
except:
    pass

# 4. Проверка содержимого Authenticate.php
print("\n[4] Проверка Authenticate.php:")
stdin, stdout, stderr = ssh.exec_command("grep -E 'api/|expectsJson' /root/shannon/backend-laravel/app/Http/Middleware/Authenticate.php | head -3")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output if output else "Не найдено")
except:
    pass

ssh.close()
print("\n=== Диагностика завершена ===")

