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

print("Загрузка исправлений авторизации...")

sftp = ssh.open_sftp()

# api.ts
print("[1] Загрузка api.ts...")
with open("template/src/services/api.ts", 'r', encoding='utf-8') as f:
    content = f.read()
with sftp.file("/root/shannon/template/src/services/api.ts", 'w') as rf:
    rf.write(content)
print("OK")

# AuthContext.tsx
print("[2] Загрузка AuthContext.tsx...")
with open("template/src/contexts/AuthContext.tsx", 'r', encoding='utf-8') as f:
    content = f.read()
with sftp.file("/root/shannon/template/src/contexts/AuthContext.tsx", 'w') as rf:
    rf.write(content)
print("OK")

sftp.close()

# Пересборка
print("\n[3] Пересборка фронтенда...")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/template && npm run build 2>&1 | tail -5")
stdout.channel.settimeout(15)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    if 'built in' in output or '✓' in output:
        print("✓ Фронтенд пересобран")
    else:
        print(output[-500:])
except:
    print("Сборка запущена...")

ssh.close()
print("\nГотово!")


