#!/usr/bin/env python3
"""
Финальный запуск backend
"""

import paramiko
import time

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ЗАПУСК BACKEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Останавливаем все
        print("\n1. ОСТАНОВКА:")
        ssh.exec_command("pkill -f 'uvicorn'")
        ssh.exec_command("pkill -f 'python.*app.main'")
        ssh.exec_command("pkill -f 'python.*run.py'")
        time.sleep(2)
        print("  [OK] Остановлено")
        
        # 2. Запускаем через uvicorn с socketio_app
        print("\n2. ЗАПУСК:")
        cmd = "cd /root/shannon/backend && source venv/bin/activate 2>/dev/null && nohup python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 > /tmp/shannon_backend.log 2>&1 &"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print("  Команда выполнена")
        time.sleep(5)
        
        # 3. Проверяем процесс
        print("\n3. ПРОВЕРКА:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'python.*uvicorn.*socketio_app' | grep -v grep")
        proc = stdout.read().decode('utf-8', errors='replace')
        if proc:
            print(f"  [OK] Процесс запущен:")
            print(f"    {proc[:200]}")
        else:
            print("  [ERROR] Процесс не найден")
            print("  Проверяю логи...")
            stdin, stdout, stderr = ssh.exec_command("tail -30 /tmp/shannon_backend.log 2>/dev/null")
            logs = stdout.read().decode('utf-8', errors='replace')
            if logs:
                print("  Логи:")
                for line in logs.strip().split('\n')[-15:]:
                    if line:
                        safe_line = line.encode('ascii', 'replace').decode('ascii')
                        print(f"    {safe_line}")
        
        # 4. Проверяем порт
        print("\n4. ПРОВЕРКА ПОРТА:")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("netstat -tlnp 2>/dev/null | grep ':8000' || ss -tlnp 2>/dev/null | grep ':8000'")
        port = stdout.read().decode('utf-8', errors='replace')
        if port:
            print(f"  [OK] Порт 8000 слушается")
            print(f"    {port[:150]}")
        else:
            print("  [ERROR] Порт не слушается")
        
        # 5. Тестируем API
        print("\n5. ТЕСТ API:")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/health 2>&1")
        health = stdout.read().decode('utf-8', errors='replace')
        if health:
            print(f"  /health: {health[:200]}")
        
        stdin, stdout, stderr = ssh.exec_command("curl -s -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"513277\"}' 2>&1")
        login = stdout.read().decode('utf-8', errors='replace')
        if login:
            if 'access_token' in login:
                print("  /api/auth/login: [OK] Работает!")
            else:
                print(f"  /api/auth/login: {login[:200]}")
        
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТ")
        print("="*60)
        
        if proc and port:
            print("\n[SUCCESS] Backend запущен и работает!")
            print("\nДоступен по адресу:")
            print("  https://72.56.79.153/api")
            print("\nДля входа используйте:")
            print("  Логин: admin")
            print("  Пароль: 513277")
        else:
            print("\n[ERROR] Backend не запустился")
            print("Проверьте логи: tail -f /tmp/shannon_backend.log")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

