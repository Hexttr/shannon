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

# Проверка dist
stdin, stdout, stderr = ssh.exec_command("test -f /root/shannon/template/dist/index.html && echo 'EXISTS' || echo 'NOT_FOUND'")
result = stdout.read().decode('utf-8').strip()
print(f"index.html: {result}")

# Проверка последних строк сборки
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/template && npm run build 2>&1 | tail -5")
output = stdout.read().decode('utf-8', errors='ignore')
print("\nПоследние строки сборки:")
print(output)

ssh.close()

