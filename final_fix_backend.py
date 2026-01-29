#!/usr/bin/env python3
"""
Финальное исправление backend
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
        print("1. Пересоздаю venv...")
        ssh.exec_command("rm -rf /root/shannon/backend/venv")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && python3 -m venv venv")
        time.sleep(5)
        
        print("2. Устанавливаю зависимости через python3 -m pip...")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && venv/bin/python3 -m pip install --upgrade pip setuptools wheel -q 2>&1")
        time.sleep(3)
        
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && venv/bin/python3 -m pip install -r requirements.txt 2>&1 | tail -5")
        install_output = stdout.read().decode('utf-8', errors='replace')
        print(f"  {install_output}")
        
        print("3. Проверяю установку...")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && venv/bin/python3 -c 'import uvicorn; print(\"OK\")' 2>&1")
        check = stdout.read().decode('utf-8', errors='replace')
        check_err = stderr.read().decode('utf-8', errors='replace')
        if check_err:
            print(f"  [ERROR] {check_err[:200]}")
            return
        print(f"  {check}")
        
        print("4. Запускаю backend...")
        cmd = "cd /root/shannon/backend && venv/bin/python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 > /tmp/shannon_backend.log 2>&1 &"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        time.sleep(5)
        
        print("5. Проверяю процесс...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'python.*uvicorn.*socketio_app' | grep -v grep")
        proc = stdout.read().decode('utf-8', errors='replace')
        if proc:
            print(f"  [OK] Процесс запущен")
        else:
            print("  [ERROR] Процесс не найден")
            stdin, stdout, stderr = ssh.exec_command("tail -20 /tmp/shannon_backend.log 2>/dev/null")
            logs = stdout.read().decode('utf-8', errors='replace')
            if logs:
                print("  Логи:")
                for line in logs.strip().split('\n')[-10:]:
                    if line:
                        safe_line = line.encode('ascii', 'replace').decode('ascii')
                        print(f"    {safe_line}")
            return
        
        stdin, stdout, stderr = ssh.exec_command("netstat -tlnp 2>/dev/null | grep ':8000' || ss -tlnp 2>/dev/null | grep ':8000'")
        port = stdout.read().decode('utf-8', errors='replace')
        if port:
            print(f"  [OK] Порт 8000 слушается")
        
        print("\n" + "="*60)
        print("[SUCCESS] Backend запущен!")
        print("="*60)
        print("\nДоступен: https://72.56.79.153/api")
        print("Логин: admin")
        print("Пароль: 513277")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

