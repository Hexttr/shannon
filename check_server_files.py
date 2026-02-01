#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка актуальности файлов на сервере
"""

import sys
import os
import paramiko
from server_utils import SERVER_HOST, SERVER_USER, SERVER_PASSWORD, SERVER_PORT

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def check_and_upload_files():
    """Проверяет и загружает файлы"""
    print("Проверка и загрузка файлов на сервер...")
    
    # Список файлов для проверки
    files_to_check = [
        ("backend-laravel/app/Http/Middleware/Authenticate.php", "/root/shannon/backend-laravel/app/Http/Middleware/Authenticate.php"),
        ("backend-laravel/app/Services/ClaudeApiService.php", "/root/shannon/backend-laravel/app/Services/ClaudeApiService.php"),
        ("template/src/pages/Pentests.tsx", "/root/shannon/template/src/pages/Pentests.tsx"),
        ("template/vite.config.ts", "/root/shannon/template/vite.config.ts"),
        ("template/src/App.tsx", "/root/shannon/template/src/App.tsx"),
        ("template/src/main.tsx", "/root/shannon/template/src/main.tsx"),
    ]
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    try:
        sftp = ssh.open_sftp()
        
        for local_path, remote_path in files_to_check:
            if not os.path.exists(local_path):
                print(f"[SKIP] {local_path} не найден локально")
                continue
            
            print(f"\n[1] Проверка {os.path.basename(local_path)}...")
            
            # Читаем локальный файл
            with open(local_path, 'r', encoding='utf-8') as f:
                local_content = f.read()
            
            # Проверяем существует ли файл на сервере
            try:
                with sftp.file(remote_path, 'r') as remote_file:
                    remote_content = remote_file.read().decode('utf-8')
                
                if local_content == remote_content:
                    print(f"[OK] {os.path.basename(local_path)} актуален")
                else:
                    print(f"[UPDATE] {os.path.basename(local_path)} устарел, обновляю...")
                    with sftp.file(remote_path, 'w') as remote_file:
                        remote_file.write(local_content)
                    print(f"[OK] {os.path.basename(local_path)} обновлен")
            except FileNotFoundError:
                print(f"[CREATE] {os.path.basename(local_path)} не найден на сервере, создаю...")
                # Создаем директорию если нужно
                remote_dir = os.path.dirname(remote_path)
                ssh.exec_command(f"mkdir -p {remote_dir}")
                
                with sftp.file(remote_path, 'w') as remote_file:
                    remote_file.write(local_content)
                print(f"[OK] {os.path.basename(local_path)} создан")
        
        sftp.close()
        
        # Проверка ошибок Laravel
        print("\n[2] Проверка последних ошибок Laravel:")
        stdin, stdout, stderr = ssh.exec_command("tail -30 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'ERROR|Exception' | tail -10")
        output = stdout.read().decode('utf-8')
        if output.strip():
            print(output)
        else:
            print("Нет ошибок")
        
        # Проверка доступности API
        print("\n[3] Тест API /auth/login:")
        stdin, stdout, stderr = ssh.exec_command("curl -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' 2>&1 | head -5")
        output = stdout.read().decode('utf-8')
        if 'token' in output:
            print("[OK] API работает")
        else:
            print(f"[ERROR] Проблема с API: {output[-200:]}")
        
        print("\n[OK] Проверка завершена!")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    check_and_upload_files()

