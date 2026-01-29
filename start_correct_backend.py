#!/usr/bin/env python3
"""
Запуск правильного Python backend
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
        # Останавливаем все процессы uvicorn
        print("Останавливаю старые процессы...")
        ssh.exec_command("pkill -f 'uvicorn.*app.main'")
        time.sleep(2)
        
        # Запускаем правильный backend
        print("Запускаю Python backend...")
        cmd = "cd /root/shannon/backend && source venv/bin/activate && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/shannon_backend.log 2>&1 &"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        time.sleep(3)
        
        # Проверяем
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'python.*uvicorn.*app.main' | grep -v grep")
        status = stdout.read().decode('utf-8', errors='replace')
        if status:
            print(f"[OK] Backend запущен: {status[:100]}")
        else:
            print("[ERROR] Backend не запустился")
            stdin, stdout, stderr = ssh.exec_command("tail -30 /tmp/shannon_backend.log")
            logs = stdout.read().decode('utf-8', errors='replace')
            print(f"Логи: {logs[:500]}")
        
        # Проверяем статус пентеста
        print("\nСтатус пентеста:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, status, current_step FROM pentests WHERE id = 2;'")
        pentest_status = stdout.read().decode('utf-8', errors='replace')
        print(f"  {pentest_status}")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

