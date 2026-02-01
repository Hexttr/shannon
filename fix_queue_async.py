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

print("=== Настройка асинхронной очереди ===\n")

# Проверяем есть ли таблица jobs
print("[1] Проверка таблицы jobs:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo Schema::hasTable('jobs') ? 'EXISTS' : 'NOT_EXISTS';\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output)
except:
    pass

# Добавляем QUEUE_CONNECTION=database в .env
print("\n[2] Настройка .env:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && grep -q 'QUEUE_CONNECTION' .env && echo 'EXISTS' || echo 'NOT_EXISTS'")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8').strip()
    if 'NOT_EXISTS' in output:
        print("Добавление QUEUE_CONNECTION=database...")
        ssh.exec_command("cd /root/shannon/backend-laravel && echo 'QUEUE_CONNECTION=database' >> .env")
        print("✓ Добавлено")
    else:
        print("Обновление QUEUE_CONNECTION...")
        ssh.exec_command("cd /root/shannon/backend-laravel && sed -i 's/^QUEUE_CONNECTION=.*/QUEUE_CONNECTION=database/' .env || echo 'QUEUE_CONNECTION=database' >> .env")
        print("✓ Обновлено")
except:
    pass

# Проверяем миграции
print("\n[3] Проверка миграций:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 5 php artisan migrate --force 2>&1 | tail -5")
stdout.channel.settimeout(6)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Создаем systemd сервис для queue worker
print("\n[4] Создание сервиса для queue worker...")
queue_service = """[Unit]
Description=Shannon Laravel Queue Worker
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/shannon/backend-laravel
ExecStart=/usr/bin/php /root/shannon/backend-laravel/artisan queue:work database --sleep=3 --tries=3 --max-time=3600
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

sftp = ssh.open_sftp()
with sftp.file("/etc/systemd/system/shannon-queue.service", 'w') as f:
    f.write(queue_service)
sftp.close()

# Перезагружаем systemd и запускаем сервис
print("[5] Запуск queue worker...")
ssh.exec_command("systemctl daemon-reload")
ssh.exec_command("systemctl enable shannon-queue.service")
ssh.exec_command("systemctl restart shannon-queue.service")

# Проверяем статус
print("\n[6] Статус queue worker:")
stdin, stdout, stderr = ssh.exec_command("systemctl status shannon-queue.service --no-pager | head -10")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

# Перезапускаем Laravel чтобы применить изменения .env
print("\n[7] Перезапуск Laravel...")
ssh.exec_command("systemctl restart shannon-laravel.service")

ssh.close()
print("\n=== Готово ===")


