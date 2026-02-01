#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import paramiko
import time

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("72.56.79.153", port=22, username="root", password="m8J@2_6whwza6U", timeout=10)

print("=== Перезапуск Laravel и тест ===\n")

print("[1] Перезапуск Laravel...")
stdin, stdout, stderr = ssh.exec_command("systemctl restart shannon-laravel.service")
stdout.channel.settimeout(3)
stdout.read()
print("✓ Перезапущен")

time.sleep(3)

print("\n[2] Тест API...")
stdin, stdout, stderr = ssh.exec_command("timeout 5 curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' | head -3")
stdout.channel.settimeout(6)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if 'token' in output:
        print("✓ API работает")
    else:
        print(f"Ответ: {output[:200]}")
except:
    print("Таймаут")

ssh.close()
print("\n=== Готово ===")


