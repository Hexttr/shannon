#!/usr/bin/env python3
"""
Исправление запуска backend
"""

import paramiko
import time

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ИСПРАВЛЕНИЕ ЗАПУСКА BACKEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Останавливаем все процессы
        print("\n1. ОСТАНОВКА ВСЕХ ПРОЦЕССОВ:")
        ssh.exec_command("pkill -f 'uvicorn'")
        ssh.exec_command("pkill -f 'python.*app.main'")
        time.sleep(2)
        print("  [OK] Процессы остановлены")
        
        # 2. Проверяем структуру проекта
        print("\n2. ПРОВЕРКА СТРУКТУРЫ:")
        stdin, stdout, stderr = ssh.exec_command("ls -la /root/shannon/backend/app/ | head -10")
        structure = stdout.read().decode('utf-8', errors='replace')
        print(f"  {structure[:300]}")
        
        # 3. Проверяем main.py
        print("\n3. ПРОВЕРКА MAIN.PY:")
        stdin, stdout, stderr = ssh.exec_command("test -f /root/shannon/backend/app/main.py && echo 'OK' || echo 'НЕ НАЙДЕНО'")
        main_check = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"  main.py: {main_check}")
        
        # 4. Пробуем запустить напрямую
        print("\n4. ЗАПУСК BACKEND:")
        cmd = "cd /root/shannon/backend && source venv/bin/activate 2>/dev/null && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/shannon_backend.log 2>&1 &"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        time.sleep(5)
        
        # 5. Проверяем процесс
        print("\n5. ПРОВЕРКА ПРОЦЕССА:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'python.*uvicorn|python.*app.main' | grep -v grep")
        proc = stdout.read().decode('utf-8', errors='replace')
        if proc:
            print(f"  [OK] Процесс найден: {proc[:150]}")
        else:
            print("  [ERROR] Процесс не найден")
            print("  Проверяю логи...")
            stdin, stdout, stderr = ssh.exec_command("tail -50 /tmp/shannon_backend.log 2>/dev/null")
            logs = stdout.read().decode('utf-8', errors='replace')
            if logs:
                print("  Логи:")
                for line in logs.strip().split('\n')[-20:]:
                    if line:
                        safe_line = line.encode('ascii', 'replace').decode('ascii')
                        print(f"    {safe_line[:150]}")
        
        # 6. Проверяем порт
        print("\n6. ПРОВЕРКА ПОРТА:")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("netstat -tlnp 2>/dev/null | grep ':8000' || ss -tlnp 2>/dev/null | grep ':8000'")
        port = stdout.read().decode('utf-8', errors='replace')
        if port:
            print(f"  [OK] Порт слушается: {port[:100]}")
        else:
            print("  [ERROR] Порт не слушается")
        
        # 7. Тестируем API
        print("\n7. ТЕСТИРОВАНИЕ API:")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/api/health 2>&1 | head -5 || curl -s http://localhost:8000/health 2>&1 | head -5")
        api_test = stdout.read().decode('utf-8', errors='replace')
        if api_test:
            print(f"  Ответ API: {api_test[:200]}")
        
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТ")
        print("="*60)
        
        if proc:
            print("\n[SUCCESS] Backend запущен")
            print("Проверьте доступность:")
            print("  https://72.56.79.153/api/auth/login")
        else:
            print("\n[ERROR] Backend не запустился")
            print("Проверьте логи: tail -f /tmp/shannon_backend.log")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

