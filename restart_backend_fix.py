#!/usr/bin/env python3
"""
Запуск backend с исправлением проблем
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
        # 1. Останавливаем старые процессы
        print("\n1. ОСТАНОВКА СТАРЫХ ПРОЦЕССОВ:")
        ssh.exec_command("pkill -f 'uvicorn.*app.main'")
        time.sleep(2)
        print("  [OK] Старые процессы остановлены")
        
        # 2. Проверяем виртуальное окружение
        print("\n2. ПРОВЕРКА ВИРТУАЛЬНОГО ОКРУЖЕНИЯ:")
        stdin, stdout, stderr = ssh.exec_command("test -d /root/shannon/backend/venv && echo 'OK' || echo 'НЕ НАЙДЕНО'")
        venv_check = stdout.read().decode('utf-8', errors='replace').strip()
        if venv_check == 'OK':
            print("  [OK] Виртуальное окружение найдено")
        else:
            print("  [WARNING] Виртуальное окружение не найдено, создаю...")
            stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && python3 -m venv venv")
            time.sleep(5)
            print("  [OK] Виртуальное окружение создано")
        
        # 3. Устанавливаем зависимости если нужно
        print("\n3. ПРОВЕРКА ЗАВИСИМОСТЕЙ:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && source venv/bin/activate && python3 -c 'import uvicorn' 2>&1")
        uvicorn_check = stdout.read().decode('utf-8', errors='replace')
        if 'No module named' in uvicorn_check or 'ModuleNotFoundError' in uvicorn_check:
            print("  [WARNING] Зависимости не установлены, устанавливаю...")
            stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && source venv/bin/activate && pip install -q -r requirements.txt 2>&1 | tail -5")
            install_output = stdout.read().decode('utf-8', errors='replace')
            print(f"  {install_output}")
        else:
            print("  [OK] Зависимости установлены")
        
        # 4. Запускаем backend
        print("\n4. ЗАПУСК BACKEND:")
        cmd = "cd /root/shannon/backend && source venv/bin/activate && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/shannon_backend.log 2>&1 &"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        time.sleep(5)
        
        # 5. Проверяем что backend запустился
        print("\n5. ПРОВЕРКА ЗАПУСКА:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'python.*uvicorn.*app.main' | grep -v grep")
        backend_proc = stdout.read().decode('utf-8', errors='replace')
        if backend_proc:
            print(f"  [OK] Backend запущен:")
            print(f"    {backend_proc[:150]}")
        else:
            print("  [ERROR] Backend не запустился, проверяю логи...")
            stdin, stdout, stderr = ssh.exec_command("tail -30 /tmp/shannon_backend.log 2>/dev/null")
            error_logs = stdout.read().decode('utf-8', errors='replace')
            if error_logs:
                print("  Логи ошибок:")
                print(error_logs[:800])
        
        # 6. Проверяем порт
        print("\n6. ПРОВЕРКА ПОРТА:")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("netstat -tlnp 2>/dev/null | grep ':8000' || ss -tlnp 2>/dev/null | grep ':8000'")
        port_check = stdout.read().decode('utf-8', errors='replace')
        if port_check:
            print(f"  [OK] Порт 8000 слушается: {port_check[:100]}")
        else:
            print("  [WARNING] Порт 8000 не слушается")
        
        # 7. Проверяем доступность API
        print("\n7. ПРОВЕРКА API:")
        stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/health 2>/dev/null || curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health 2>/dev/null || echo 'недоступен'")
        api_check = stdout.read().decode('utf-8', errors='replace').strip()
        if api_check and api_check != 'недоступен':
            print(f"  [OK] API отвечает: код {api_check}")
        else:
            print("  [WARNING] API не отвечает")
        
        print("\n" + "="*60)
        print("ГОТОВО")
        print("="*60)
        print("\nBackend должен быть доступен по адресу:")
        print("  http://72.56.79.153:8000")
        print("  https://72.56.79.153/api")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

