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

print("=== Проверка ошибок Laravel ===\n")

# Проверяем последние ошибки
print("[1] Последние ошибки Laravel:")
stdin, stdout, stderr = ssh.exec_command("tail -200 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'ERROR|Exception|Fatal' | tail -50")
stdout.channel.settimeout(10)
try:
    errors = stdout.read().decode('utf-8', errors='ignore')
    if errors.strip():
        print(errors)
    else:
        print("Нет ошибок ERROR/Exception/Fatal")
except:
    pass

# Проверяем все последние записи
print("\n[2] Последние записи в логе:")
stdin, stdout, stderr = ssh.exec_command("tail -100 /root/shannon/backend-laravel/storage/logs/laravel.log")
stdout.channel.settimeout(10)
try:
    recent = stdout.read().decode('utf-8', errors='ignore')
    print(recent[-2000:])  # Последние 2000 символов
except:
    pass

# Проверяем статус Laravel
print("\n[3] Статус Laravel:")
stdin, stdout, stderr = ssh.exec_command("systemctl status shannon-laravel.service --no-pager | head -20")
stdout.channel.settimeout(5)
try:
    status = stdout.read().decode('utf-8', errors='ignore')
    print(status)
except:
    pass

ssh.close()


