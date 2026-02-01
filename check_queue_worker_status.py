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

print("=== Проверка Queue Worker ===\n")

# Статус queue worker
print("[1] Статус queue worker:")
stdin, stdout, stderr = ssh.exec_command("systemctl status shannon-queue.service --no-pager | head -15")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Процессы queue worker
print("\n[2] Процессы queue worker:")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'queue:work' | grep -v grep")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    if output.strip():
        print(output)
    else:
        print("✗ Queue worker не запущен!")
except:
    pass

# Логи queue worker
print("\n[3] Последние логи queue worker:")
stdin, stdout, stderr = ssh.exec_command("journalctl -u shannon-queue.service -n 30 --no-pager | tail -20")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    if output.strip():
        print(output)
    else:
        print("Нет логов")
except:
    pass

# Перезапуск queue worker если не работает
print("\n[4] Перезапуск queue worker...")
stdin, stdout, stderr = ssh.exec_command("systemctl restart shannon-queue.service")
stdout.channel.settimeout(3)
stdout.read()

import time
time.sleep(2)

# Проверяем статус после перезапуска
print("\n[5] Статус после перезапуска:")
stdin, stdout, stderr = ssh.exec_command("systemctl is-active shannon-queue.service")
stdout.channel.settimeout(3)
try:
    status = stdout.read().decode('utf-8').strip()
    print(f"Статус: {status}")
except:
    pass

ssh.close()

