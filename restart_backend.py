#!/usr/bin/env python3
"""
Перезапуск backend
"""

import paramiko
import time

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Останавливаем старый процесс
        print("Останавливаю старый процесс...")
        ssh.exec_command("pkill -f 'uvicorn.*app.main'")
        time.sleep(2)
        
        # Запускаем новый
        print("Запускаю backend...")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && source venv/bin/activate && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &")
        time.sleep(3)
        
        # Проверяем
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'uvicorn.*app.main' | grep -v grep")
        status = stdout.read().decode('utf-8', errors='replace')
        if status:
            print("[OK] Backend запущен")
        else:
            print("[ERROR] Backend не запустился")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
