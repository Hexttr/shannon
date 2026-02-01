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

print("=== Загрузка отрефакторенного Services.tsx ===\n")

# Загружаем файл
sftp = ssh.open_sftp()
with open("template/src/pages/Services.tsx", 'r', encoding='utf-8') as f:
    content = f.read()
with sftp.file("/root/shannon/template/src/pages/Services.tsx", 'w') as rf:
    rf.write(content.encode('utf-8'))
sftp.close()
print("✓ Файл загружен")

# Пересобираем фронтенд
print("\nПересборка фронтенда...")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/template && npm run build 2>&1 | tail -30")
stdout.channel.settimeout(120)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    if 'built in' in output.lower() or ('vite' in output.lower() and 'error' not in output.lower()):
        print("✓ Фронтенд пересобран успешно")
    else:
        # Проверяем есть ли ошибки
        if 'error' in output.lower():
            print("✗ Ошибки сборки:")
            lines = output.split('\n')
            for line in lines:
                if 'error' in line.lower():
                    print(f"  {line}")
        else:
            print("Вывод сборки:")
            print(output[-500:])
except:
    print("Таймаут сборки")

ssh.close()
print("\n=== Готово ===")


