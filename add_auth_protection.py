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

print("=== Добавление защиты авторизации ===\n")

# Читаем AuthContext
print("[1] Проверка AuthContext...")
stdin, stdout, stderr = ssh.exec_command("grep -A 10 'checkAuth\|getMe' /root/shannon/template/src/contexts/AuthContext.tsx | head -20")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Проверяем что API interceptor правильно обрабатывает ошибки
print("\n[2] Проверка API interceptor...")
stdin, stdout, stderr = ssh.exec_command("grep -A 5 'interceptors.response' /root/shannon/template/src/services/api.ts")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

ssh.close()

