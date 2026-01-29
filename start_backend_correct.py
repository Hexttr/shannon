#!/usr/bin/env python3
"""
Правильный запуск backend с WebSocket
"""

import paramiko
import time

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ПРАВИЛЬНЫЙ ЗАПУСК BACKEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Останавливаем все процессы
        print("\n1. ОСТАНОВКА ПРОЦЕССОВ:")
        ssh.exec_command("pkill -f 'uvicorn'")
        ssh.exec_command("pkill -f 'python.*app.main'")
        time.sleep(2)
        print("  [OK] Процессы остановлены")
        
        # 2. Проверяем логи
        print("\n2. ПРОВЕРКА ЛОГОВ:")
        stdin, stdout, stderr = ssh.exec_command("tail -30 /tmp/shannon_backend.log 2>/dev/null")
        logs = stdout.read().decode('utf-8', errors='replace')
        if logs:
            print("  Последние логи:")
            for line in logs.strip().split('\n')[-15:]:
                if line:
                    safe_line = line.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_line[:150]}")
        
        # 3. Запускаем через run.py (правильный способ)
        print("\n3. ЗАПУСК ЧЕРЕЗ run.py:")
        cmd = "cd /root/shannon/backend && source venv/bin/activate 2>/dev/null && nohup python3 run.py > /tmp/shannon_backend.log 2>&1 &"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        time.sleep(5)
        
        # 4. Проверяем процесс
        print("\n4. ПРОВЕРКА ПРОЦЕССА:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'python.*run.py|python.*uvicorn' | grep -v grep")
        proc = stdout.read().decode('utf-8', errors='replace')
        if proc:
            print(f"  [OK] Процесс найден:")
            print(f"    {proc[:150]}")
        else:
            print("  [ERROR] Процесс не найден")
            print("  Проверяю логи запуска...")
            stdin, stdout, stderr = ssh.exec_command("tail -50 /tmp/shannon_backend.log 2>/dev/null")
            error_logs = stdout.read().decode('utf-8', errors='replace')
            if error_logs:
                print("  Логи ошибок:")
                for line in error_logs.strip().split('\n')[-20:]:
                    if line:
                        safe_line = line.encode('ascii', 'replace').decode('ascii')
                        print(f"    {safe_line[:150]}")
        
        # 5. Альтернативный способ - через uvicorn напрямую
        if not proc:
            print("\n5. АЛЬТЕРНАТИВНЫЙ ЗАПУСК (uvicorn):")
            cmd2 = "cd /root/shannon/backend && source venv/bin/activate 2>/dev/null && nohup python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 > /tmp/shannon_backend.log 2>&1 &"
            stdin, stdout, stderr = ssh.exec_command(cmd2)
            time.sleep(5)
            
            stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'python.*uvicorn.*socketio_app' | grep -v grep")
            proc2 = stdout.read().decode('utf-8', errors='replace')
            if proc2:
                print(f"  [OK] Процесс запущен:")
                print(f"    {proc2[:150]}")
            else:
                print("  [ERROR] Не удалось запустить")
        
        # 6. Проверяем порт
        print("\n6. ПРОВЕРКА ПОРТА:")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("netstat -tlnp 2>/dev/null | grep ':8000' || ss -tlnp 2>/dev/null | grep ':8000'")
        port = stdout.read().decode('utf-8', errors='replace')
        if port:
            print(f"  [OK] Порт 8000 слушается:")
            print(f"    {port[:150]}")
        else:
            print("  [ERROR] Порт 8000 не слушается")
        
        # 7. Тестируем API
        print("\n7. ТЕСТИРОВАНИЕ API:")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/health 2>&1")
        health = stdout.read().decode('utf-8', errors='replace')
        if health:
            print(f"  Ответ /health: {health[:200]}")
        
        stdin, stdout, stderr = ssh.exec_command("curl -s -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"test\",\"password\":\"test\"}' 2>&1 | head -3")
        login_test = stdout.read().decode('utf-8', errors='replace')
        if login_test:
            print(f"  Ответ /api/auth/login: {login_test[:200]}")
        
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТ")
        print("="*60)
        
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'python.*uvicorn|python.*run.py' | grep -v grep")
        final_check = stdout.read().decode('utf-8', errors='replace')
        
        if final_check:
            print("\n[SUCCESS] Backend запущен!")
            print("\nПроверьте доступность:")
            print("  https://72.56.79.153/api/auth/login")
            print("\nДля входа используйте:")
            print("  Логин: admin")
            print("  Пароль: 513277")
        else:
            print("\n[ERROR] Backend не запустился")
            print("\nПроверьте логи:")
            print("  tail -f /tmp/shannon_backend.log")
            print("\nВозможные причины:")
            print("  1. Ошибки в коде")
            print("  2. Отсутствие зависимостей")
            print("  3. Проблемы с конфигурацией (.env)")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

