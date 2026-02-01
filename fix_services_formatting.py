#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import paramiko
import re

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("72.56.79.153", port=22, username="root", password="m8J@2_6whwza6U", timeout=10)

print("=== Исправление форматирования Services.tsx ===\n")

# Читаем файл с сервера
sftp = ssh.open_sftp()
with sftp.file("/root/shannon/template/src/pages/Services.tsx", 'r') as f:
    content = f.read().decode('utf-8', errors='ignore')

# Исправляем проблемные места
# 1. Исправляем пустой массив на строке 30-35
content = re.sub(r'const ids: string\[\] = \[\s+\];', 'const ids: string[] = [];', content, flags=re.MULTILINE)

# 2. Исправляем пустой массив на строке 36-40
content = re.sub(r'map\[pentestId\] = \[\s+\];', 'map[pentestId] = [];', content, flags=re.MULTILINE)

# 3. Исправляем разрыв строки в updateMutation
content = re.sub(r'id: string;\s+data: UpdateServiceRequest', 'id: string; data: UpdateServiceRequest', content, flags=re.MULTILINE)

# Записываем обратно
with sftp.file("/root/shannon/template/src/pages/Services.tsx", 'w') as f:
    f.write(content.encode('utf-8'))

sftp.close()
print("✓ Форматирование исправлено")

# Пересобираем
print("\nПересборка...")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/template && npm run build 2>&1 | tail -30")
stdout.channel.settimeout(60)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    if 'built in' in output.lower() or 'vite' in output.lower() and 'error' not in output.lower():
        print("✓ Фронтенд пересобран успешно")
    else:
        print("Вывод сборки:")
        print(output[-800:])
except:
    print("Таймаут")

ssh.close()


