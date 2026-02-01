#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка отсутствующих файлов на сервер
"""

import sys
import os
import paramiko
from server_utils import SERVER_HOST, SERVER_USER, SERVER_PASSWORD, SERVER_PORT

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def upload_missing_files():
    """Загружает отсутствующие файлы"""
    print("Загрузка отсутствующих файлов...")
    
    files_to_upload = [
        ("template/src/utils/severity.ts", "/root/shannon/template/src/utils/severity.ts"),
    ]
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    try:
        sftp = ssh.open_sftp()
        
        for local_path, remote_path in files_to_upload:
            if os.path.exists(local_path):
                print(f"\n[1] Загрузка {local_path}...")
                with open(local_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Создаем директорию если нужно
                remote_dir = os.path.dirname(remote_path)
                ssh.exec_command(f"mkdir -p {remote_dir}")
                
                with sftp.file(remote_path, 'w') as remote_file:
                    remote_file.write(content)
                
                print(f"[OK] {os.path.basename(local_path)} загружен")
            else:
                print(f"[WARNING] {local_path} не найден локально")
        
        sftp.close()
        
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
        output = '\n'.join(output_lines)
        
        if output_lines:
            print('\n'.join(output_lines[-30:]))
        
        if exit_status == 0:
            print("\n[OK] Фронтенд успешно собран!")
            stdin, stdout, stderr = ssh.exec_command("test -f /root/shannon/template/dist/index.html && ls -lh /root/shannon/template/dist/index.html || echo 'NOT FOUND'")
            result = stdout.read().decode('utf-8').strip()
            print(f"\n[3] Результат:\n{result}")
            return True
        else:
            print("\n[ERROR] Ошибка сборки!")
            return False
            
    finally:
        ssh.close()

if __name__ == "__main__":
    success = upload_missing_files()
    sys.exit(0 if success else 1)

