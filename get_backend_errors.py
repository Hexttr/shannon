#!/usr/bin/env python3
"""
Получение ошибок backend
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
        print("Проверяю логи backend...")
        stdin, stdout, stderr = ssh.exec_command("tail -50 /tmp/shannon_backend.log 2>/dev/null")
        logs = stdout.read().decode('utf-8', errors='replace')
        
        if logs:
            print("ЛОГИ BACKEND:")
            print("="*60)
            for line in logs.strip().split('\n'):
                if line:
                    try:
                        safe_line = line.encode('ascii', 'replace').decode('ascii')
                        print(safe_line)
                    except:
                        print(line[:100])
        else:
            print("Логи не найдены")
            
            # Пробуем запустить и сразу получить ошибки
            print("\nПробую запустить и получить ошибки...")
            stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && source venv/bin/activate 2>&1 && python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 2>&1 | head -50")
            output = stdout.read().decode('utf-8', errors='replace')
            errors = stderr.read().decode('utf-8', errors='replace')
            
            if errors:
                print("ОШИБКИ:")
                print("="*60)
                for line in errors.strip().split('\n')[:50]:
                    if line:
                        try:
                            safe_line = line.encode('ascii', 'replace').decode('ascii')
                            print(safe_line)
                        except:
                            print(line[:100])
            
            if output:
                print("\nВЫВОД:")
                print("="*60)
                for line in output.strip().split('\n')[:50]:
                    if line:
                        try:
                            safe_line = line.encode('ascii', 'replace').decode('ascii')
                            print(safe_line)
                        except:
                            print(line[:100])
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

