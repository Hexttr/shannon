#!/usr/bin/env python3
"""
Проверка почему упал backend
"""

import paramiko

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ПРОВЕРКА BACKEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверяем процессы backend
        print("\n1. ПРОЦЕССЫ BACKEND:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'uvicorn|python.*app.main' | grep -v grep")
        processes = stdout.read().decode('utf-8', errors='replace')
        if processes:
            print("  [FOUND] Найдены процессы:")
            for proc in processes.strip().split('\n'):
                if proc:
                    print(f"    {proc[:150]}")
        else:
            print("  [ERROR] Backend не запущен!")
        
        # 2. Проверяем логи backend
        print("\n2. ЛОГИ BACKEND:")
        stdin, stdout, stderr = ssh.exec_command("tail -50 /tmp/shannon_backend.log 2>/dev/null || tail -50 /tmp/backend.log 2>/dev/null || echo 'Логи не найдены'")
        logs = stdout.read().decode('utf-8', errors='replace')
        if logs and 'не найдены' not in logs.lower():
            print("  Последние строки логов:")
            for line in logs.strip().split('\n')[-20:]:
                if line:
                    safe_line = line.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_line[:150]}")
        else:
            print("  [INFO] Логи не найдены")
        
        # 3. Проверяем порт 8000
        print("\n3. ПОРТ 8000:")
        stdin, stdout, stderr = ssh.exec_command("netstat -tlnp 2>/dev/null | grep ':8000' || ss -tlnp 2>/dev/null | grep ':8000' || echo 'Порт не слушается'")
        port_status = stdout.read().decode('utf-8', errors='replace')
        if port_status and 'не слушается' not in port_status:
            print(f"  [OK] Порт слушается: {port_status[:100]}")
        else:
            print("  [ERROR] Порт 8000 не слушается")
        
        # 4. Проверяем синтаксис Python
        print("\n4. ПРОВЕРКА СИНТАКСИСА:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && python3 -m py_compile app/main.py 2>&1")
        syntax_check = stdout.read().decode('utf-8', errors='replace')
        syntax_errors = stderr.read().decode('utf-8', errors='replace')
        if syntax_errors:
            print(f"  [ERROR] Ошибки синтаксиса: {syntax_errors[:300]}")
        else:
            print("  [OK] Синтаксис корректен")
        
        # 5. Проверяем импорт модулей
        print("\n5. ПРОВЕРКА ИМПОРТОВ:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && python3 -c 'from app.main import app; print(\"OK\")' 2>&1")
        import_output = stdout.read().decode('utf-8', errors='replace')
        import_errors = stderr.read().decode('utf-8', errors='replace')
        if import_errors:
            print(f"  [ERROR] Ошибки импорта: {import_errors[:500]}")
        else:
            print(f"  {import_output}")
        
        # 6. Пробуем запустить backend
        print("\n6. ПРОБУЮ ЗАПУСТИТЬ BACKEND:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && timeout 5 python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 2>&1 | head -30")
        startup_output = stdout.read().decode('utf-8', errors='replace')
        startup_errors = stderr.read().decode('utf-8', errors='replace')
        if startup_errors:
            print("  [ERROR] Ошибки запуска:")
            print(startup_errors[:800])
        if startup_output:
            print("  Вывод:")
            print(startup_output[:800])
        
        # 7. Проверяем зависимости
        print("\n7. ПРОВЕРКА ЗАВИСИМОСТЕЙ:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && source venv/bin/activate && python3 -c 'import uvicorn; import fastapi; import anthropic; print(\"OK\")' 2>&1")
        deps_check = stdout.read().decode('utf-8', errors='replace')
        deps_errors = stderr.read().decode('utf-8', errors='replace')
        if deps_errors:
            print(f"  [ERROR] Ошибки зависимостей: {deps_errors[:500]}")
        else:
            print(f"  {deps_check}")
        
        # 8. Проверяем конфигурацию
        print("\n8. ПРОВЕРКА КОНФИГУРАЦИИ:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && test -f .env && echo 'OK' || echo 'Файл .env не найден'")
        env_check = stdout.read().decode('utf-8', errors='replace')
        print(f"  .env файл: {env_check.strip()}")
        
        print("\n" + "="*60)
        print("ДИАГНОСТИКА")
        print("="*60)
        
        if not processes:
            print("\n[ERROR] Backend не запущен")
            print("\nПопробую запустить backend...")
        else:
            print("\n[INFO] Backend работает")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

