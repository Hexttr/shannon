#!/usr/bin/env python3
"""
Проверка почему backend не запускается
"""

import paramiko

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Проверяем синтаксис Python
        print("1. Проверяю синтаксис Python...")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && python3 -m py_compile app/core/claude_client.py 2>&1")
        output = stdout.read().decode('utf-8', errors='replace')
        errors = stderr.read().decode('utf-8', errors='replace')
        if errors:
            print(f"  [ERROR] {errors}")
        else:
            print("  [OK] Синтаксис корректен")
        
        # Пробуем импортировать модуль
        print("\n2. Проверяю импорт модуля...")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && python3 -c 'from app.core.claude_client import ClaudeClient; print(\"OK\")' 2>&1")
        import_output = stdout.read().decode('utf-8', errors='replace')
        import_errors = stderr.read().decode('utf-8', errors='replace')
        if import_errors:
            print(f"  [ERROR] {import_errors}")
        else:
            print(f"  {import_output}")
        
        # Пробуем запустить uvicorn
        print("\n3. Пробую запустить uvicorn...")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && timeout 5 python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 2>&1 | head -20")
        uvicorn_output = stdout.read().decode('utf-8', errors='replace')
        uvicorn_errors = stderr.read().decode('utf-8', errors='replace')
        if uvicorn_errors:
            print(f"  [ERROR] {uvicorn_errors[:500]}")
        if uvicorn_output:
            print(f"  {uvicorn_output[:500]}")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

