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

print("=== Исправление таймаутов Nginx ===\n")

# Читаем текущую конфигурацию
print("[1] Чтение конфигурации...")
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-available/shannon")
stdout.channel.settimeout(5)
current_config = stdout.read().decode('utf-8', errors='ignore')

# Проверяем есть ли уже таймауты
if 'proxy_read_timeout' in current_config:
    print("Таймауты уже настроены")
    ssh.close()
    exit(0)

# Добавляем таймауты в location /api
print("[2] Добавление таймаутов...")
lines = current_config.split('\n')
new_lines = []
in_api_location = False
added_timeouts = False

for i, line in enumerate(lines):
    if 'location /api' in line:
        in_api_location = True
        new_lines.append(line)
    elif in_api_location:
        # Добавляем таймауты после последнего proxy_set_header
        if 'proxy_set_header' in line and (i == len(lines) - 1 or 'proxy_set_header' not in lines[i + 1]):
            new_lines.append(line)
            indent = ' ' * (len(line) - len(line.lstrip()))
            new_lines.append(f'{indent}proxy_read_timeout 300s;')
            new_lines.append(f'{indent}proxy_connect_timeout 60s;')
            new_lines.append(f'{indent}proxy_send_timeout 300s;')
            added_timeouts = True
        elif line.strip() == '}' and added_timeouts:
            in_api_location = False
            new_lines.append(line)
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

new_config = '\n'.join(new_lines)

# Сохраняем
sftp = ssh.open_sftp()
with sftp.file("/etc/nginx/sites-available/shannon", 'w') as f:
    f.write(new_config)
sftp.close()

# Проверяем синтаксис
print("[3] Проверка синтаксиса...")
stdin, stdout, stderr = ssh.exec_command("nginx -t")
stdout.channel.settimeout(5)
test_output = stdout.read().decode('utf-8', errors='ignore')

if 'syntax is ok' in test_output.lower():
    print("✓ Синтаксис правильный")
    print("[4] Перезагрузка Nginx...")
    stdin, stdout, stderr = ssh.exec_command("systemctl reload nginx")
    stdout.channel.settimeout(5)
    stdout.read()
    print("✓ Nginx перезагружен")
else:
    print(f"✗ Ошибка: {test_output}")

ssh.close()
print("\n=== Готово ===")


