#!/usr/bin/env python3
"""
Установка зависимостей и запуск backend
"""

import paramiko
import time

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("УСТАНОВКА ЗАВИСИМОСТЕЙ И ЗАПУСК")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Пересоздаем venv
        print("\n1. ПЕРЕСОЗДАНИЕ VENV:")
        ssh.exec_command("rm -rf /root/shannon/backend/venv")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && python3 -m venv venv")
        time.sleep(5)
        print("  [OK] venv создан")
        
        # 2. Обновляем pip
        print("\n2. ОБНОВЛЕНИЕ PIP:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && venv/bin/python3 -m pip install --upgrade pip -q 2>&1")
        pip_output = stdout.read().decode('utf-8', errors='replace')
        print("  [OK] pip обновлен")
        
        # 3. Устанавливаем зависимости
        print("\n3. УСТАНОВКА ЗАВИСИМОСТЕЙ:")
        print("  Это может занять несколько минут...")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && venv/bin/pip install -r requirements.txt 2>&1 | tail -20")
        install_output = stdout.read().decode('utf-8', errors='replace')
        if install_output:
            print("  Последние строки установки:")
            for line in install_output.strip().split('\n')[-10:]:
                if line:
                    safe_line = line.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_line[:100]}")
        print("  [OK] Зависимости установлены")
        
        # 4. Проверяем установку
        print("\n4. ПРОВЕРКА УСТАНОВКИ:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && venv/bin/python3 -c 'import uvicorn; import fastapi; import socketio; print(\"OK\")' 2>&1")
        check = stdout.read().decode('utf-8', errors='replace')
        check_err = stderr.read().decode('utf-8', errors='replace')
        if check_err:
            print(f"  [ERROR] {check_err[:300]}")
        else:
            print(f"  {check}")
        
        # 5. Запускаем backend
        print("\n5. ЗАПУСК BACKEND:")
        cmd = "cd /root/shannon/backend && venv/bin/python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 > /tmp/shannon_backend.log 2>&1 &"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        time.sleep(5)
        
        # 6. Проверяем
        print("\n6. ПРОВЕРКА:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'python.*uvicorn.*socketio_app' | grep -v grep")
        proc = stdout.read().decode('utf-8', errors='replace')
        if proc:
            print(f"  [OK] Процесс запущен")
        else:
            print("  [ERROR] Процесс не найден")
            stdin, stdout, stderr = ssh.exec_command("tail -30 /tmp/shannon_backend.log 2>/dev/null")
            logs = stdout.read().decode('utf-8', errors='replace')
            if logs:
                print("  Логи:")
                for line in logs.strip().split('\n')[-10:]:
                    if line:
                        safe_line = line.encode('ascii', 'replace').decode('ascii')
                        print(f"    {safe_line}")
        
        stdin, stdout, stderr = ssh.exec_command("netstat -tlnp 2>/dev/null | grep ':8000' || ss -tlnp 2>/dev/null | grep ':8000'")
        port = stdout.read().decode('utf-8', errors='replace')
        if port:
            print(f"  [OK] Порт 8000 слушается")
        
        print("\n" + "="*60)
        if proc and port:
            print("[SUCCESS] Backend запущен!")
            print("\nДоступен: https://72.56.79.153/api")
            print("Логин: admin")
            print("Пароль: 513277")
        else:
            print("[ERROR] Backend не запустился")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

