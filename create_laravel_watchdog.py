#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import paramiko

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

# Создаем systemd watchdog для автоматического перезапуска Laravel при зависании
watchdog_service = """[Unit]
Description=Shannon Laravel Watchdog
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /root/shannon/watchdog_laravel.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

watchdog_script = """#!/usr/bin/env python3
import time
import subprocess
import requests

def check_laravel():
    try:
        response = requests.get('http://localhost:8000/up', timeout=2)
        return response.status_code == 200
    except:
        return False

while True:
    if not check_laravel():
        print("Laravel не отвечает, перезапускаю...")
        subprocess.run(['systemctl', 'restart', 'shannon-laravel.service'])
        time.sleep(5)
    time.sleep(30)
"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("72.56.79.153", port=22, username="root", password="m8J@2_6whwza6U", timeout=10)

print("Создание watchdog для Laravel...")

# Создаем скрипт watchdog
sftp = ssh.open_sftp()
with sftp.file("/root/shannon/watchdog_laravel.py", 'w') as f:
    f.write(watchdog_script)
sftp.close()

# Делаем исполняемым
ssh.exec_command("chmod +x /root/shannon/watchdog_laravel.py")

print("✓ Watchdog создан")
print("\nПримечание: Watchdog можно включить позже если нужно")
print("Для включения: systemctl enable shannon-watchdog.service")

ssh.close()

