#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка исправленного main.tsx и пересборка
"""

import sys
import os
import paramiko
from server_utils import SERVER_HOST, SERVER_USER, SERVER_PASSWORD, SERVER_PORT

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def upload_and_rebuild():
    """Загружает исправленный main.tsx и пересобирает"""
    print("Загрузка исправленного main.tsx...")
    
    local_file = "template/src/main.tsx"
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
        remote_path = "/root/shannon/template/src/main.tsx"
        
        with sftp.file(remote_path, 'w') as remote_file:
            remote_file.write(content)
        
        sftp.close()
        print("[OK] main.tsx загружен")
        
        # Пересборка
        print("\n[2] Пересборка фронтенда...")
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
        
        if output_lines:
            print('\n'.join(output_lines[-20:]))
        
        if exit_status == 0:
            print("\n[OK] Фронтенд успешно пересобран!")
            return True
        else:
            print("\n[ERROR] Ошибка сборки!")
            return False
            
    finally:
        ssh.close()

if __name__ == "__main__":
    success = upload_and_rebuild()
    sys.exit(0 if success else 1)

