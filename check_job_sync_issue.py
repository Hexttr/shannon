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

print("=== Проверка синхронного выполнения Job ===\n")

# Проверяем код StartPentestAction
print("[1] Проверка StartPentestAction:")
stdin, stdout, stderr = ssh.exec_command("grep -A 2 'dispatch' /root/shannon/backend-laravel/app/Domain/Pentests/Actions/StartPentestAction.php")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Проверяем что RunPentestJob implements ShouldQueue
print("\n[2] Проверка RunPentestJob:")
stdin, stdout, stderr = ssh.exec_command("grep -E 'ShouldQueue|dispatch' /root/shannon/backend-laravel/app/Domain/Pentests/Jobs/RunPentestJob.php")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Проверяем конфигурацию очереди еще раз
print("\n[3] Проверка конфигурации очереди:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo config('queue.default'); echo '|'; echo config('queue.connections.database.driver');\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output)
except:
    pass

# Проверяем последние ошибки при выполнении Job
print("\n[4] Ошибки выполнения Job:")
stdin, stdout, stderr = ssh.exec_command("tail -100 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -A 5 'RunPentestJob\\|addLog\\|Cannot assign' | tail -20")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if output:
        print(output)
    else:
        print("Нет ошибок")
except:
    pass

ssh.close()

