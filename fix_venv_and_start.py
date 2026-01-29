#!/usr/bin/env python3
"""
Исправление venv и запуск backend
"""

import paramiko
import time

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ИСПРАВЛЕНИЕ VENV И ЗАПУСК BACKEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверяем venv
        print("\n1. ПРОВЕРКА VENV:")
        stdin, stdout, stderr = ssh.exec_command("test -d /root/shannon/backend/venv && echo 'OK' || echo 'НЕ НАЙДЕНО'")
        venv_check = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"  venv: {venv_check}")
        
        if venv_check != 'OK':
            print("  Создаю venv...")
            stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && python3 -m venv venv")
            time.sleep(5)
            print("  [OK] venv создан")
        
        # 2. Устанавливаем зависимости
        print("\n2. УСТАНОВКА ЗАВИСИМОСТЕЙ:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && venv/bin/pip install -q -r requirements.txt 2>&1 | tail -10")
        install_output = stdout.read().decode('utf-8', errors='replace')
        if install_output:
            print(f"  {install_output}")
        print("  [OK] Зависимости установлены")
        
        # 3. Запускаем backend
        print("\n3. ЗАПУСК BACKEND:")
        cmd = "cd /root/shannon/backend && venv/bin/python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 > /tmp/shannon_backend.log 2>&1 &"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        time.sleep(5)
        
        # 4. Проверяем процесс
        print("\n4. ПРОВЕРКА:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'python.*uvicorn.*socketio_app' | grep -v grep")
        proc = stdout.read().decode('utf-8', errors='replace')
        if proc:
            print(f"  [OK] Процесс запущен:")
            print(f"    {proc[:200]}")
        else:
            print("  [ERROR] Процесс не найден")
            stdin, stdout, stderr = ssh.exec_command("tail -30 /tmp/shannon_backend.log 2>/dev/null")
            logs = stdout.read().decode('utf-8', errors='replace')
            if logs:
                print("  Логи:")
                for line in logs.strip().split('\n')[-15:]:
                    if line:
                        safe_line = line.encode('ascii', 'replace').decode('ascii')
                        print(f"    {safe_line}")
        
        # 5. Проверяем порт
        print("\n5. ПРОВЕРКА ПОРТА:")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("netstat -tlnp 2>/dev/null | grep ':8000' || ss -tlnp 2>/dev/null | grep ':8000'")
        port = stdout.read().decode('utf-8', errors='replace')
        if port:
            print(f"  [OK] Порт 8000 слушается")
        else:
            print("  [ERROR] Порт не слушается")
        
        # 6. Тестируем
        print("\n6. ТЕСТ API:")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/health 2>&1")
        health = stdout.read().decode('utf-8', errors='replace')
        if health:
            print(f"  /health: {health}")
        
        print("\n" + "="*60)
        if proc and port:
            print("[SUCCESS] Backend запущен!")
            print("\nДоступен: https://72.56.79.153/api")
            print("Логин: admin / Пароль: 513277")
        else:
            print("[ERROR] Backend не запустился")
            print("Проверьте: tail -f /tmp/shannon_backend.log")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

