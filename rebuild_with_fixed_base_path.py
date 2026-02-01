#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пересборка фронтенда с исправленным base path
"""

import sys
import os
import paramiko
from server_utils import SERVER_HOST, SERVER_USER, SERVER_PASSWORD, SERVER_PORT

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def rebuild_frontend():
    """Пересобирает фронтенд с исправленным base path"""
    print("Пересборка фронтенда с исправленным base path...")
    
    # Загружаем исправленные файлы
    files_to_upload = [
        ("template/vite.config.ts", "/root/shannon/template/vite.config.ts"),
        ("template/src/App.tsx", "/root/shannon/template/src/App.tsx"),
    ]
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    try:
        sftp = ssh.open_sftp()
        
        for local_path, remote_path in files_to_upload:
            if os.path.exists(local_path):
                print(f"\n[1] Загрузка {os.path.basename(local_path)}...")
                with open(local_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                with sftp.file(remote_path, 'w') as remote_file:
                    remote_file.write(content)
                
                print(f"[OK] {os.path.basename(local_path)} загружен")
        
        sftp.close()
        
        # Удаляем старый dist
        print("\n[2] Удаление старого dist...")
        ssh.exec_command("rm -rf /root/shannon/template/dist")
        
        # Пересборка
        print("\n[3] Пересборка фронтенда...")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/template && npm run build 2>&1")
        
        output_lines = []
        while True:
            line = stdout.readline()
            if not line:
                break
            output_lines.append(line.rstrip())
            if len(output_lines) % 30 == 0:
                print(f"  Собрано строк: {len(output_lines)}...")
        
        exit_status = stdout.channel.recv_exit_status()
        output = '\n'.join(output_lines)
        
        if output_lines:
            print('\n'.join(output_lines[-30:]))
        
        if exit_status == 0:
            print("\n[OK] Фронтенд успешно собран!")
            
            # Проверка index.html
            print("\n[4] Проверка index.html:")
            stdin, stdout, stderr = ssh.exec_command("head -15 /root/shannon/template/dist/index.html")
            result = stdout.read().decode('utf-8').strip()
            print(result)
            
            # Проверка что пути правильные
            if '/app/assets/' in result:
                print("\n[WARNING] Все еще есть пути /app/assets/ - нужно проверить")
            elif '/assets/' in result:
                print("\n[OK] Пути исправлены на /assets/")
            
            return True
        else:
            print("\n[ERROR] Ошибка сборки!")
            return False
            
    finally:
        ssh.close()

if __name__ == "__main__":
    success = rebuild_frontend()
    sys.exit(0 if success else 1)

