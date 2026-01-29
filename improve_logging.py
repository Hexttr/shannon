#!/usr/bin/env python3
"""
Улучшение логирования в pentest_engine.py
"""

import paramiko
import os

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def upload_file(sftp, local_path, remote_path):
    """Загружает файл через SFTP"""
    print(f"Загружаю {local_path} -> {remote_path}")
    sftp.put(local_path, remote_path)

def main():
    print("="*60)
    print("УЛУЧШЕНИЕ ЛОГИРОВАНИЯ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    sftp = ssh.open_sftp()
    
    try:
        # Загружаем исправленный файл
        print("\n1. Загружаю улучшенный pentest_engine.py...")
        upload_file(sftp, 'backend/app/core/pentest_engine.py', '/root/shannon/backend/app/core/pentest_engine.py')
        
        sftp.close()
        
        # Перезапускаем backend
        print("\n2. Перезапускаю backend...")
        stdin, stdout, stderr = ssh.exec_command("pkill -f 'python.*uvicorn.*app.main:socketio_app' || true")
        stdout.channel.recv_exit_status()
        
        import time
        time.sleep(2)
        
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 > /tmp/shannon-backend.log 2>&1 &")
        stdout.channel.recv_exit_status()
        
        time.sleep(3)
        
        # Проверяем что backend запустился
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'uvicorn|python.*app.main' | grep -v grep")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            print("[OK] Backend перезапущен")
        else:
            print("[ERROR] Backend не запустился")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print("\nЛогирование улучшено. Новые пентесты будут показывать больше информации.")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

