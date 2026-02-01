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

print("=== Принудительная настройка database очереди ===\n")

# Проверяем .env
print("[1] Проверка .env:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && grep QUEUE_CONNECTION .env")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output)
    if 'database' not in output:
        print("✗ Неправильная конфигурация")
except:
    pass

# Устанавливаем QUEUE_CONNECTION=database
print("\n[2] Установка QUEUE_CONNECTION=database...")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && sed -i 's/^QUEUE_CONNECTION=.*/QUEUE_CONNECTION=database/' .env || echo 'QUEUE_CONNECTION=database' >> .env")
stdout.channel.settimeout(3)
stdout.read()

# Проверяем что установлено
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && grep QUEUE_CONNECTION .env")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8').strip()
    print(f"✓ {output}")
except:
    pass

# Очищаем кэш конфигурации
print("\n[3] Очистка кэша...")
ssh.exec_command("cd /root/shannon/backend-laravel && php artisan config:clear && php artisan cache:clear")

# Перезапускаем Laravel
print("[4] Перезапуск Laravel...")
ssh.exec_command("systemctl restart shannon-laravel.service")

import time
time.sleep(3)

# Проверяем конфигурацию
print("\n[5] Проверка конфигурации после перезапуска:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo config('queue.default');\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    queue_type = output.split('\n')[-1] if '\n' in output else output
    print(f"Очередь: {queue_type}")
    if 'database' in queue_type.lower():
        print("✓ Очередь настроена правильно")
    else:
        print("✗ Очередь все еще sync")
except:
    pass

ssh.close()
print("\n=== Готово ===")


