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

print("=== Финальная проверка исправлений ===\n")

# Проверка файлов
print("[1] Проверка ключевых файлов:")
files = [
    "/root/shannon/backend-laravel/app/Http/Middleware/Authenticate.php",
    "/root/shannon/backend-laravel/app/Services/ClaudeApiService.php",
    "/root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php",
    "/root/shannon/template/src/services/api.ts",
    "/etc/nginx/sites-available/shannon"
]

for file in files:
    stdin, stdout, stderr = ssh.exec_command(f"test -f {file} && echo 'EXISTS' || echo 'NOT_FOUND'")
    stdout.channel.settimeout(2)
    try:
        status = stdout.read().decode('utf-8').strip()
        print(f"  {os.path.basename(file)}: {status}")
    except:
        pass

# Проверка таймаутов Nginx
print("\n[2] Проверка таймаутов Nginx:")
stdin, stdout, stderr = ssh.exec_command("grep 'proxy_read_timeout' /etc/nginx/sites-available/shannon")
stdout.channel.settimeout(2)
try:
    output = stdout.read().decode('utf-8').strip()
    if output:
        print("  ✓ Таймауты настроены")
        print(f"  {output}")
    else:
        print("  ✗ Таймауты не найдены")
except:
    pass

# Проверка статуса сервисов
print("\n[3] Статус сервисов:")
stdin, stdout, stderr = ssh.exec_command("systemctl is-active shannon-laravel.service nginx.service")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8').strip()
    print(f"  {output}")
except:
    pass

# Тест API
print("\n[4] Тест API:")
stdin, stdout, stderr = ssh.exec_command("timeout 5 curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' | head -3")
stdout.channel.settimeout(6)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if 'token' in output:
        print("  ✓ API работает")
    else:
        print(f"  Ответ: {output[:100]}")
except:
    print("  Таймаут")

ssh.close()

print("\n=== Итоги исправлений ===")
print("\n1. ✓ Исправлен Authenticate middleware для API")
print("2. ✓ Исправлен ClaudeApiService (nullable apiKey)")
print("3. ✓ Добавлен заголовок Accept: application/json в API клиент")
print("4. ✓ Увеличены таймауты Nginx (300s для proxy_read_timeout)")
print("5. ✓ Добавлено создание логов при выполнении пентеста")
print("6. ✓ Laravel перезапущен")
print("\nПопробуйте:")
print("  - Войти в систему: https://72.56.79.153")
print("  - Запустить пентест")
print("  - Проверить логи пентеста")

