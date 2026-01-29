#!/usr/bin/env python3
"""
Проверка логов backend для выяснения причины падения
"""

import paramiko

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ПРОВЕРКА ЛОГОВ BACKEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверяем логи
        print("\n1. ЛОГИ BACKEND:")
        stdin, stdout, stderr = ssh.exec_command("tail -100 /tmp/shannon_backend.log 2>/dev/null")
        logs = stdout.read().decode('utf-8', errors='replace')
        if logs:
            print("  Последние 100 строк:")
            for line in logs.strip().split('\n'):
                if line:
                    safe_line = line.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_line}")
        else:
            print("  [INFO] Логи не найдены, проверяю другие места...")
            stdin, stdout, stderr = ssh.exec_command("find /tmp -name '*backend*.log' -o -name '*shannon*.log' 2>/dev/null | head -5")
            log_files = stdout.read().decode('utf-8', errors='replace')
            if log_files:
                print(f"  Найдены файлы логов: {log_files}")
                for log_file in log_files.strip().split('\n'):
                    if log_file:
                        stdin, stdout, stderr = ssh.exec_command(f"tail -20 {log_file} 2>/dev/null")
                        file_logs = stdout.read().decode('utf-8', errors='replace')
                        if file_logs:
                            print(f"\n  {log_file}:")
                            for line in file_logs.strip().split('\n')[-10:]:
                                if line:
                                    safe_line = line.encode('ascii', 'replace').decode('ascii')
                                    print(f"    {safe_line[:150]}")
        
        # 2. Пробуем запустить и сразу посмотреть ошибки
        print("\n2. ТЕСТОВЫЙ ЗАПУСК:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && source venv/bin/activate 2>/dev/null && timeout 3 python3 run.py 2>&1 | head -30")
        test_output = stdout.read().decode('utf-8', errors='replace')
        test_errors = stderr.read().decode('utf-8', errors='replace')
        if test_errors:
            print("  Ошибки:")
            for line in test_errors.strip().split('\n')[:30]:
                if line:
                    safe_line = line.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_line}")
        if test_output:
            print("  Вывод:")
            for line in test_output.strip().split('\n')[:30]:
                if line:
                    safe_line = line.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_line}")
        
        # 3. Проверяем зависимости
        print("\n3. ПРОВЕРКА ЗАВИСИМОСТЕЙ:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && source venv/bin/activate 2>/dev/null && python3 -c 'import uvicorn; import fastapi; import socketio; import anthropic; print(\"OK\")' 2>&1")
        deps = stdout.read().decode('utf-8', errors='replace')
        deps_err = stderr.read().decode('utf-8', errors='replace')
        if deps_err:
            print(f"  Ошибки: {deps_err[:500]}")
        else:
            print(f"  {deps}")
        
        # 4. Проверяем .env файл
        print("\n4. ПРОВЕРКА .ENV:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && test -f .env && echo 'OK' || echo 'НЕ НАЙДЕНО'")
        env_check = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"  Файл .env: {env_check}")
        
        if env_check == 'OK':
            stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && grep -E 'SECRET_KEY|ANTHROPIC_API_KEY|SSH_HOST' .env | sed 's/=.*/=***/'")
            env_vars = stdout.read().decode('utf-8', errors='replace')
            if env_vars:
                print("  Переменные (скрыты):")
                for line in env_vars.strip().split('\n'):
                    if line:
                        print(f"    {line}")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

