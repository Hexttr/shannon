#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка исправленного Authenticate middleware
"""

import sys
import os
import paramiko
from server_utils import SERVER_HOST, SERVER_USER, SERVER_PASSWORD, SERVER_PORT

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def upload_fixed_middleware():
    """Загружает исправленный middleware"""
    print("Загрузка исправленного Authenticate middleware...")
    
    local_file = "backend-laravel/app/Http/Middleware/Authenticate.php"
    if not os.path.exists(local_file):
        print(f"[ERROR] Файл {local_file} не найден")
        return False
    
    with open(local_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    try:
        sftp = ssh.open_sftp()
        remote_path = "/root/shannon/backend-laravel/app/Http/Middleware/Authenticate.php"
        
        with sftp.file(remote_path, 'w') as remote_file:
            remote_file.write(content)
        
        sftp.close()
        print("[OK] Authenticate.php загружен")
        
        # Перезапуск Laravel сервиса не требуется, изменения применятся автоматически
        print("\n[OK] Изменения применены (Laravel автоматически подхватит изменения)")
        
        # Тест API
        print("\n[2] Тест API создания пентеста:")
        stdin, stdout, stderr = ssh.exec_command("curl -X POST http://localhost:8000/api/pentests -H 'Content-Type: application/json' -H 'Authorization: Bearer test' -d '{\"name\":\"Test Pentest\",\"config\":{\"targetUrl\":\"https://example.com\"}}' 2>&1 | head -10")
        output = stdout.read().decode('utf-8')
        print(output)
        
        return True
        
    finally:
        ssh.close()

if __name__ == "__main__":
    upload_fixed_middleware()


