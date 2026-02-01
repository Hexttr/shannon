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

print("=== Проверка зависания Laravel ===\n")

# Проверка процессов Laravel
print("[1] Процессы Laravel:")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'php.*artisan serve' | grep -v grep")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output if output else "Процессы не найдены")
except:
    pass

# Проверка использования ресурсов
print("\n[2] Использование ресурсов:")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'php.*artisan serve' | grep -v grep | awk '{print $3, $4, $6}'")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if output:
        print(f"CPU%, MEM%, RSS: {output}")
except:
    pass

# Проверка подключений к порту 8000
print("\n[3] Подключения к порту 8000:")
stdin, stdout, stderr = ssh.exec_command("netstat -an | grep ':8000' | wc -l")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8').strip()
    print(f"Активных подключений: {output}")
except:
    pass

# Проверка базы данных
print("\n[4] Проверка базы данных:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo DB::connection()->getPdo() ? 'OK' : 'FAIL';\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output)
except:
    print("Таймаут проверки БД")

ssh.close()


