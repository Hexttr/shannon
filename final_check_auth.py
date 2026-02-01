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

print("Проверка ошибок авторизации...")
stdin, stdout, stderr = ssh.exec_command("tail -20 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'ERROR|Exception|auth' | tail -5")
output = stdout.read().decode('utf-8', errors='ignore')
if output.strip():
    print(output)
else:
    print("Нет ошибок в логах")

print("\nТест API /auth/login:")
stdin, stdout, stderr = ssh.exec_command("curl -s -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' | python3 -m json.tool 2>&1 | head -10")
output = stdout.read().decode('utf-8', errors='ignore')
print(output)

ssh.close()
print("\nПроверка завершена")

