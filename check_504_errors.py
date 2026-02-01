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

print("=== Проверка ошибок 504 и таймаутов ===\n")

# Проверка ошибок 504 в Nginx
print("[1] Ошибки 504 в Nginx:")
stdin, stdout, stderr = ssh.exec_command("tail -50 /var/log/nginx/error.log | grep -E '504|timeout|upstream' | tail -10")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if output:
        print(output)
    else:
        print("Нет ошибок 504")
except:
    pass

# Проверка таймаутов в Nginx конфигурации
print("\n[2] Таймауты в Nginx конфигурации:")
stdin, stdout, stderr = ssh.exec_command("grep -E 'proxy_read_timeout|proxy_connect_timeout|proxy_send_timeout|fastcgi_read_timeout' /etc/nginx/sites-available/shannon")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if output:
        print(output)
    else:
        print("Таймауты не настроены (используются значения по умолчанию)")
except:
    pass

# Проверка последних ошибок Laravel
print("\n[3] Последние ошибки Laravel:")
stdin, stdout, stderr = ssh.exec_command("tail -50 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'ERROR|Exception|timeout|Timeout' | tail -10")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if output:
        print(output)
    else:
        print("Нет ошибок")
except:
    pass

# Проверка времени ответа API
print("\n[4] Тест времени ответа API:")
stdin, stdout, stderr = ssh.exec_command("time curl -s -w '\\nTime: %{time_total}s\\n' -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' | head -5")
stdout.channel.settimeout(10)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except Exception as e:
    print(f"Ошибка: {e}")

ssh.close()

