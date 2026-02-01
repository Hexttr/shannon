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

print("=== Отладка API ответа ===\n")

# Тест с Accept заголовком
print("[1] Тест с Accept: application/json:")
stdin, stdout, stderr = ssh.exec_command("timeout 3 curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' | head -10")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output[:500])
    if '<html' in output or '<!DOCTYPE' in output:
        print("\n✗ API возвращает HTML вместо JSON!")
except Exception as e:
    print(f"Ошибка: {e}")

# Проверка последних ошибок Laravel
print("\n[2] Последние ошибки Laravel:")
stdin, stdout, stderr = ssh.exec_command("tail -50 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'ERROR|Exception' | tail -10")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if output:
        print(output)
    else:
        print("Нет ошибок")
except:
    pass

# Проверка что роуты зарегистрированы
print("\n[3] Проверка роутов API:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && php artisan route:list | grep 'api/auth' | head -5")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output if output else "Роуты не найдены")
except:
    pass

ssh.close()


