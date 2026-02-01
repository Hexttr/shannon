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

print("=== Сохранение systemd service файла ===\n")

# Читаем service файл с сервера
stdin, stdout, stderr = ssh.exec_command("cat /etc/systemd/system/shannon-queue.service")
stdout.channel.settimeout(5)
service_content = stdout.read().decode('utf-8', errors='ignore')

# Сохраняем локально
os.makedirs("systemd", exist_ok=True)
with open("systemd/shannon-queue.service", 'w', encoding='utf-8') as f:
    f.write(service_content)

print("✓ Service файл сохранен в systemd/shannon-queue.service")
print("\nСодержимое:")
print(service_content)

ssh.close()


