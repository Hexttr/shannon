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

print("=== Проверка ClaudeApiService на сервере ===\n")

# Проверяем содержимое файла на сервере
print("[1] Проверка ClaudeApiService.php:")
stdin, stdout, stderr = ssh.exec_command("head -20 /root/shannon/backend-laravel/app/Services/ClaudeApiService.php | grep -E 'apiKey|private'")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
    if '?string' in output:
        print("✓ Файл исправлен (nullable)")
    elif 'string $apiKey' in output and '?string' not in output:
        print("✗ Файл НЕ исправлен (не nullable)")
except:
    pass

ssh.close()

