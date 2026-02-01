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

print("=== Проверка конфигурации очереди ===\n")

# Проверка .env
print("[1] Конфигурация очереди в .env:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && grep -E 'QUEUE_CONNECTION|QUEUE_DRIVER' .env || echo 'Не найдено'")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output)
except:
    pass

# Проверка config/queue.php
print("\n[2] Конфигурация очереди в config/queue.php:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && grep -A 5 'default' config/queue.php | head -10")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Проверка что RunPentestJob выполняется синхронно
print("\n[3] Проверка RunPentestJob:")
stdin, stdout, stderr = ssh.exec_command("grep -E 'ShouldQueue|dispatch' /root/shannon/backend-laravel/app/Domain/Pentests/Actions/StartPentestAction.php")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

ssh.close()


