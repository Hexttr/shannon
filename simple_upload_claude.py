#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простая загрузка исправленного ClaudeApiService
"""

import sys
import os
import paramiko

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

local_file = "backend-laravel/app/Services/ClaudeApiService.php"
with open(local_file, 'r', encoding='utf-8') as f:
    content = f.read()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("72.56.79.153", port=22, username="root", password="m8J@2_6whwza6U", timeout=10)

sftp = ssh.open_sftp()
with sftp.file("/root/shannon/backend-laravel/app/Services/ClaudeApiService.php", 'w') as remote_file:
    remote_file.write(content)
sftp.close()
ssh.close()

print("[OK] ClaudeApiService.php загружен")


