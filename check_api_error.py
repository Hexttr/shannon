#!/usr/bin/env python3
"""
Проверка ошибки API
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
        print("Проверяю логи ошибок backend...")
        stdin, stdout, stderr = ssh.exec_command("tail -50 /var/log/shannon-backend-error.log 2>/dev/null")
        error_logs = stdout.read().decode('utf-8', errors='replace')
        
        if error_logs:
            print("ОШИБКИ BACKEND:")
            print("="*60)
            for line in error_logs.strip().split('\n'):
                if line:
                    try:
                        safe_line = line.encode('ascii', 'replace').decode('ascii')
                        print(safe_line)
                    except:
                        print(line[:150])
        else:
            print("Логи ошибок не найдены, проверяю обычные логи...")
            stdin, stdout, stderr = ssh.exec_command("tail -100 /var/log/shannon-backend.log 2>/dev/null | grep -A 10 -B 5 'Error\\|Exception\\|Traceback'")
            error_in_logs = stdout.read().decode('utf-8', errors='replace')
            if error_in_logs:
                print("ОШИБКИ В ЛОГАХ:")
                print("="*60)
                for line in error_in_logs.strip().split('\n'):
                    if line:
                        try:
                            safe_line = line.encode('ascii', 'replace').decode('ascii')
                            print(safe_line)
                        except:
                            print(line[:150])
        
        # Проверяю структуру step_progress в БД
        print("\n" + "="*60)
        print("ПРОВЕРКА ДАННЫХ В БД:")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, step_progress FROM pentests WHERE id = 2;'")
        step_progress_data = stdout.read().decode('utf-8', errors='replace')
        print(f"step_progress для пентеста 2: {step_progress_data}")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

