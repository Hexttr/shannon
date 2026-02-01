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

print("=== Загрузка исправленных файлов ===\n")

files_to_upload = [
    ("template/src/pages/Services.tsx", "/root/shannon/template/src/pages/Services.tsx"),
    ("template/src/services/serviceApi.ts", "/root/shannon/template/src/services/serviceApi.ts"),
    ("template/src/types/index.ts", "/root/shannon/template/src/types/index.ts"),
]

sftp = ssh.open_sftp()

for local_path, remote_path in files_to_upload:
    print(f"Загрузка {local_path}...")
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with sftp.file(remote_path, 'w') as rf:
        rf.write(content)
    print(f"✓ {local_path} загружен")

sftp.close()

# Пересобираем фронтенд
print("\nПересборка фронтенда...")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/template && npm run build 2>&1 | tail -20")
stdout.channel.settimeout(60)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    if 'built in' in output.lower() or 'vite' in output.lower():
        print("✓ Фронтенд пересобран")
    else:
        print("Вывод сборки:")
        print(output[-500:])
except:
    print("Таймаут сборки (возможно долго собирается)")

ssh.close()
print("\n=== Готово ===")

