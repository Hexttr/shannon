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

stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-available/shannon")
stdout.channel.settimeout(5)
config = stdout.read().decode('utf-8', errors='ignore')

with open("nginx_shannon.conf", 'w', encoding='utf-8') as f:
    f.write(config)

print("Конфигурация сохранена в nginx_shannon.conf")
ssh.close()


