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

print("=== Запуск Queue Worker ===\n")

# Проверяем ошибки
print("[1] Проверка ошибок queue worker:")
stdin, stdout, stderr = ssh.exec_command("systemctl status shannon-queue.service --no-pager | tail -10")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Проверяем .env
print("\n[2] Проверка QUEUE_CONNECTION в .env:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && grep QUEUE_CONNECTION .env")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output)
except:
    pass

# Запускаем queue worker вручную для теста
print("\n[3] Тест запуска queue worker:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan queue:work database --once 2>&1 | head -5")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Запускаем сервис
print("\n[4] Запуск сервиса queue worker...")
stdin, stdout, stderr = ssh.exec_command("systemctl start shannon-queue.service")
stdout.channel.settimeout(3)
stdout.read()

time.sleep(2)

# Проверяем статус
print("\n[5] Статус queue worker:")
stdin, stdout, stderr = ssh.exec_command("systemctl is-active shannon-queue.service")
stdout.channel.settimeout(3)
try:
    status = stdout.read().decode('utf-8').strip()
    print(f"Статус: {status}")
    if status == 'active':
        print("✓ Queue worker запущен")
    else:
        print("✗ Queue worker не запущен")
        # Проверяем логи
        stdin, stdout, stderr = ssh.exec_command("journalctl -u shannon-queue.service -n 10 --no-pager")
        stdout.channel.settimeout(3)
        try:
            logs = stdout.read().decode('utf-8', errors='ignore')
            print(f"\nЛоги:\n{logs}")
        except:
            pass
except:
    pass

ssh.close()


