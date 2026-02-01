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

print("=== Проверка ошибки сборки ===\n")

# Проверяем полный вывод сборки
print("[1] Полный вывод сборки:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/template && npm run build 2>&1")
stdout.channel.settimeout(120)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    # Ищем ошибки
    if 'error' in output.lower():
        print("Ошибки найдены:")
        lines = output.split('\n')
        for i, line in enumerate(lines):
            if 'error' in line.lower() or 'failed' in line.lower():
                print(f"  {i}: {line}")
                # Показываем контекст
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    if j != i:
                        print(f"    {j}: {lines[j]}")
    else:
        print(output[-1000:])
except:
    print("Таймаут")

ssh.close()


