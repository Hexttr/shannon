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
print("[1] Чтение текущей конфигурации Nginx...")
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-available/shannon")
stdout.channel.settimeout(5)
try:
    current_config = stdout.read().decode('utf-8', errors='ignore')
    print("Конфигурация прочитана")
except:
    print("Ошибка чтения конфигурации")
    ssh.close()
    exit(1)

# Добавляем таймауты в location /api
if 'proxy_read_timeout' not in current_config:
    print("\n[2] Добавление таймаутов в конфигурацию...")
    
    # Заменяем location /api блок
    import re
    new_config = re.sub(
        r'(location /api \{[^}]*proxy_pass[^}]*)(\})',
        r'\1\n        proxy_read_timeout 300s;\n        proxy_connect_timeout 60s;\n        proxy_send_timeout 300s;\n\2',
        current_config,
        flags=re.DOTALL
    )
    
    # Если не нашлось, добавляем вручную
    if new_config == current_config:
        # Находим location /api и добавляем таймауты после proxy_set_header
        lines = current_config.split('\n')
        new_lines = []
        in_api_location = False
        api_location_indent = 0
        
        for i, line in enumerate(lines):
            if 'location /api' in line:
                in_api_location = True
                api_location_indent = len(line) - len(line.lstrip())
            elif in_api_location and line.strip().startswith('location ') and 'location /api' not in line:
                # Добавляем таймауты перед закрытием блока
                indent = ' ' * (api_location_indent + 8)
                new_lines.append(f'{indent}proxy_read_timeout 300s;')
                new_lines.append(f'{indent}proxy_connect_timeout 60s;')
                new_lines.append(f'{indent}proxy_send_timeout 300s;')
                in_api_location = False
            elif in_api_location and line.strip() == '}' and i > 0 and 'location' not in lines[i-1]:
                # Перед закрывающей скобкой добавляем таймауты
                indent = ' ' * (len(line) - len(line.lstrip()) - 4)
                new_lines.append(f'{indent}proxy_read_timeout 300s;')
                new_lines.append(f'{indent}proxy_connect_timeout 60s;')
                new_lines.append(f'{indent}proxy_send_timeout 300s;')
                in_api_location = False
            
            new_lines.append(line)
        
        new_config = '\n'.join(new_lines)
    
    # Сохраняем новую конфигурацию
    sftp = ssh.open_sftp()
    with sftp.file("/tmp/shannon_nginx_new.conf", 'w') as f:
        f.write(new_config)
    sftp.close()
    
    # Проверяем синтаксис
    print("[3] Проверка синтаксиса...")
    stdin, stdout, stderr = ssh.exec_command("nginx -t -c /tmp/shannon_nginx_new.conf 2>&1")
    stdout.channel.settimeout(5)
    test_output = stdout.read().decode('utf-8', errors='ignore')
    
    if 'syntax is ok' in test_output.lower():
        print("✓ Синтаксис правильный")
        
        # Копируем конфигурацию
        print("[4] Применение конфигурации...")
        ssh.exec_command("cp /tmp/shannon_nginx_new.conf /etc/nginx/sites-available/shannon")
        
        # Перезагружаем Nginx
        print("[5] Перезагрузка Nginx...")
        stdin, stdout, stderr = ssh.exec_command("nginx -t && systemctl reload nginx")
        stdout.channel.settimeout(5)
        reload_output = stdout.read().decode('utf-8', errors='ignore')
        if 'successful' in reload_output.lower() or 'test is successful' in reload_output.lower():
            print("✓ Nginx перезагружен")
        else:
            print(f"Выход: {reload_output}")
    else:
        print(f"✗ Ошибка синтаксиса: {test_output}")
else:
    print("Таймауты уже настроены")

ssh.close()
print("\n=== Готово ===")


