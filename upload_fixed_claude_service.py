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

print("=== Загрузка исправленного ClaudeApiService ===\n")

# Загружаем файл
sftp = ssh.open_sftp()
with open("backend-laravel/app/Services/ClaudeApiService.php", 'r', encoding='utf-8') as f:
    content = f.read()
with sftp.file("/root/shannon/backend-laravel/app/Services/ClaudeApiService.php", 'w') as rf:
    rf.write(content)
sftp.close()
print("✓ Файл загружен")

# Перезапускаем Laravel
print("\nПерезапуск Laravel...")
ssh.exec_command("systemctl restart shannon-laravel.service")
ssh.exec_command("systemctl restart shannon-queue.service")

ssh.close()
print("✓ Сервисы перезапущены")
print("\n⚠ ВАЖНО: API ключ НЕ сохранен в git (он только в .env на сервере)")
