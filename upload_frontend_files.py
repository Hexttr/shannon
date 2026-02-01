#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("72.56.79.153", port=22, username="root", password="m8J@2_6whwza6U", timeout=10)
sftp = ssh.open_sftp()

# App.tsx
print("Загрузка App.tsx...")
with open("template/src/App.tsx", 'r', encoding='utf-8') as f:
    content = f.read()
with sftp.file("/root/shannon/template/src/App.tsx", 'w') as rf:
    rf.write(content)
print("OK")

# vite.config.ts
print("Загрузка vite.config.ts...")
with open("template/vite.config.ts", 'r', encoding='utf-8') as f:
    content = f.read()
with sftp.file("/root/shannon/template/vite.config.ts", 'w') as rf:
    rf.write(content)
print("OK")

# main.tsx
print("Загрузка main.tsx...")
with open("template/src/main.tsx", 'r', encoding='utf-8') as f:
    content = f.read()
with sftp.file("/root/shannon/template/src/main.tsx", 'w') as rf:
    rf.write(content)
print("OK")

sftp.close()

# Пересборка
print("Пересборка фронтенда...")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/template && npm run build 2>&1 | tail -10")
output = stdout.read().decode('utf-8')
print(output)

ssh.close()
print("Готово")


