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

print("=== Проверка конфигурации Queue Worker ===\n")

# Проверяем systemd service
print("[1] Конфигурация systemd service:")
stdin, stdout, stderr = ssh.exec_command("cat /etc/systemd/system/shannon-queue.service")
stdout.channel.settimeout(5)
try:
    service_config = stdout.read().decode('utf-8', errors='ignore')
    print(service_config)
    
    # Проверяем есть ли --timeout в команде
    if '--timeout' in service_config:
        print("\n✓ Timeout указан в systemd service")
    else:
        print("\n⚠ Timeout не указан в systemd service")
        print("Рекомендуется добавить --timeout=21600")
except:
    pass

# Проверяем конфигурацию queue.php
print("\n[2] Конфигурация queue.php (database):")
stdin, stdout, stderr = ssh.exec_command("grep -A 5 \"'database' =>\" /root/shannon/backend-laravel/config/queue.php")
stdout.channel.settimeout(5)
try:
    queue_config = stdout.read().decode('utf-8', errors='ignore')
    print(queue_config)
except:
    pass

# Проверяем текущий процесс queue worker
print("\n[3] Текущий процесс queue worker:")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'queue:work' | grep -v grep")
stdout.channel.settimeout(3)
try:
    process = stdout.read().decode('utf-8', errors='ignore')
    if process.strip():
        print(process)
        if '--timeout' in process:
            print("\n✓ Timeout указан в процессе")
        else:
            print("\n⚠ Timeout не указан в процессе")
    else:
        print("Queue worker не запущен")
except:
    pass

ssh.close()


