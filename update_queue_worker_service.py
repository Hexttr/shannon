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

print("=== Обновление Queue Worker Service ===\n")

# Читаем текущий service файл
print("[1] Чтение текущего service файла...")
stdin, stdout, stderr = ssh.exec_command("cat /etc/systemd/system/shannon-queue.service")
stdout.channel.settimeout(5)
current_config = stdout.read().decode('utf-8', errors='ignore')

# Обновляем команду ExecStart
print("[2] Обновление ExecStart...")
new_config = current_config.replace(
    'ExecStart=/usr/bin/php /root/shannon/backend-laravel/artisan queue:work database --sleep=3 --tries=3 --max-time=3600',
    'ExecStart=/usr/bin/php /root/shannon/backend-laravel/artisan queue:work database --sleep=3 --tries=3 --timeout=21600 --max-time=21600'
)

# Сохраняем обновленный файл
sftp = ssh.open_sftp()
with sftp.file("/etc/systemd/system/shannon-queue.service", 'w') as f:
    f.write(new_config.encode('utf-8'))
sftp.close()
print("✓ Service файл обновлен")

# Перезагружаем systemd и перезапускаем service
print("\n[3] Перезагрузка systemd и перезапуск service...")
ssh.exec_command("systemctl daemon-reload")
ssh.exec_command("systemctl restart shannon-queue.service")
print("✓ Service перезапущен")

# Проверяем новый процесс
print("\n[4] Проверка нового процесса:")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'queue:work' | grep -v grep")
stdout.channel.settimeout(3)
try:
    process = stdout.read().decode('utf-8', errors='ignore')
    if process.strip():
        print(process)
        if '--timeout=21600' in process:
            print("\n✓ Timeout=21600 установлен в процессе")
        if '--max-time=21600' in process:
            print("✓ Max-time=21600 установлен в процессе")
except:
    pass

# Проверяем статус
print("\n[5] Статус service:")
stdin, stdout, stderr = ssh.exec_command("systemctl status shannon-queue.service --no-pager | head -10")
stdout.channel.settimeout(5)
try:
    status = stdout.read().decode('utf-8', errors='ignore')
    print(status)
except:
    pass

ssh.close()

print("\n=== Готово ===")
print("\nQueue Worker настроен на:")
print("  - --timeout=21600 (6 часов для выполнения одного job)")
print("  - --max-time=21600 (6 часов максимальное время работы worker)")


