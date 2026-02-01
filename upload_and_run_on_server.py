#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import paramiko

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

# Создаем диагностический скрипт
diagnostic_script = """#!/bin/bash
set -e

echo "=== Проверка ошибок авторизации ==="
echo ""
echo "[1] Последние ошибки Laravel:"
tail -30 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'ERROR|Exception|auth|login' | tail -10 || echo "Нет ошибок"
echo ""
echo "[2] Тест API /auth/login:"
curl -s -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin"}' | head -5
echo ""
echo "[3] Проверка файлов:"
ls -la /root/shannon/backend-laravel/app/Http/Middleware/Authenticate.php
ls -la /root/shannon/backend-laravel/app/Services/ClaudeApiService.php
echo ""
echo "[4] Проверка содержимого Authenticate.php (первые строки):"
head -20 /root/shannon/backend-laravel/app/Http/Middleware/Authenticate.php | grep -E 'api/\*|expectsJson'
echo ""
echo "[5] Проверка статуса Laravel:"
systemctl status shannon-laravel.service --no-pager | head -5
echo ""
echo "=== Проверка завершена ==="
"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("72.56.79.153", port=22, username="root", password="m8J@2_6whwza6U", timeout=10)

# Загружаем скрипт на сервер
sftp = ssh.open_sftp()
with sftp.file("/tmp/check_auth.sh", 'w') as f:
    f.write(diagnostic_script)
sftp.close()

# Выполняем скрипт
print("Выполнение диагностики на сервере...")
stdin, stdout, stderr = ssh.exec_command("chmod +x /tmp/check_auth.sh && /tmp/check_auth.sh")
stdout.channel.settimeout(10)

output_lines = []
while True:
    line = stdout.readline()
    if not line:
        break
    output_lines.append(line.rstrip())
    if len(output_lines) <= 50:  # Показываем только первые 50 строк
        print(line.rstrip())

if len(output_lines) > 50:
    print(f"\n... (показано {len(output_lines)} строк)")

ssh.close()
print("\nДиагностика завершена")

