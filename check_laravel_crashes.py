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

print("=== Проверка падений Laravel ===\n")

# Проверка последних ошибок Laravel
print("[1] Последние ошибки Laravel:")
stdin, stdout, stderr = ssh.exec_command("tail -100 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'ERROR|Exception|Fatal|Memory' | tail -20")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if output:
        print(output)
    else:
        print("Нет критических ошибок")
except:
    pass

# Проверка процессов Laravel
print("\n[2] Процессы Laravel:")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'php.*artisan serve' | grep -v grep")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if output:
        print(output)
    else:
        print("Процессы не найдены - Laravel не запущен!")
except:
    pass

# Проверка использования памяти
print("\n[3] Использование памяти:")
stdin, stdout, stderr = ssh.exec_command("free -h")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Проверка статуса сервиса
print("\n[4] Статус сервиса Laravel:")
stdin, stdout, stderr = ssh.exec_command("systemctl status shannon-laravel.service --no-pager | head -15")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Проверка блокировок БД
print("\n[5] Проверка блокировок БД:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"try { DB::select('SELECT 1'); echo 'OK'; } catch (Exception \\$e) { echo 'ERROR'; }\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output)
except:
    print("Таймаут проверки БД")

ssh.close()

