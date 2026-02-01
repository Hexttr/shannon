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
sftp = ssh.open_sftp()

# 1. Authenticate.php
print("Загрузка Authenticate.php...")
with open("backend-laravel/app/Http/Middleware/Authenticate.php", 'r', encoding='utf-8') as f:
    content = f.read()
with sftp.file("/root/shannon/backend-laravel/app/Http/Middleware/Authenticate.php", 'w') as rf:
    rf.write(content)
print("OK")

# 2. ClaudeApiService.php
print("Загрузка ClaudeApiService.php...")
with open("backend-laravel/app/Services/ClaudeApiService.php", 'r', encoding='utf-8') as f:
    content = f.read()
with sftp.file("/root/shannon/backend-laravel/app/Services/ClaudeApiService.php", 'w') as rf:
    rf.write(content)
print("OK")

sftp.close()
ssh.close()
print("Все файлы загружены")


