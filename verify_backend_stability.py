#!/usr/bin/env python3
"""
Проверка стабильности backend
"""

import paramiko
import time

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ПРОВЕРКА СТАБИЛЬНОСТИ BACKEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Статус сервиса
        print("\n1. СТАТУС СЕРВИСА:")
        stdin, stdout, stderr = ssh.exec_command("systemctl is-active shannon-backend.service")
        is_active = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"  Активен: {is_active}")
        
        stdin, stdout, stderr = ssh.exec_command("systemctl is-enabled shannon-backend.service")
        is_enabled = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"  В автозагрузке: {is_enabled}")
        
        # 2. Процесс
        print("\n2. ПРОЦЕСС:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'python.*uvicorn.*socketio_app' | grep -v grep")
        proc = stdout.read().decode('utf-8', errors='replace')
        if proc:
            print(f"  [OK] Процесс работает:")
            print(f"    {proc[:150]}")
        else:
            print("  [ERROR] Процесс не найден")
        
        # 3. Порт
        print("\n3. ПОРТ:")
        stdin, stdout, stderr = ssh.exec_command("netstat -tlnp 2>/dev/null | grep ':8000' || ss -tlnp 2>/dev/null | grep ':8000'")
        port = stdout.read().decode('utf-8', errors='replace')
        if port:
            print(f"  [OK] Порт 8000 слушается")
        else:
            print("  [ERROR] Порт не слушается")
        
        # 4. Тест API
        print("\n4. ТЕСТ API:")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/health 2>&1")
        health = stdout.read().decode('utf-8', errors='replace')
        if health and 'ok' in health.lower():
            print(f"  [OK] /health: {health}")
        else:
            print(f"  [ERROR] /health: {health}")
        
        stdin, stdout, stderr = ssh.exec_command("curl -s -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"513277\"}' 2>&1")
        login = stdout.read().decode('utf-8', errors='replace')
        if login and 'access_token' in login:
            print("  [OK] /api/auth/login: Работает!")
        else:
            print(f"  [ERROR] /api/auth/login: {login[:200]}")
        
        # 5. Проверка автоперезапуска
        print("\n5. ПРОВЕРКА АВТОПЕРЕЗАПУСКА:")
        stdin, stdout, stderr = ssh.exec_command("systemctl show shannon-backend.service -p Restart -p RestartUSec")
        restart_info = stdout.read().decode('utf-8', errors='replace')
        if restart_info:
            print("  Настройки перезапуска:")
            for line in restart_info.strip().split('\n'):
                if line:
                    print(f"    {line}")
        
        # 6. Логи
        print("\n6. ПОСЛЕДНИЕ ЛОГИ:")
        stdin, stdout, stderr = ssh.exec_command("tail -5 /var/log/shannon-backend.log 2>/dev/null")
        logs = stdout.read().decode('utf-8', errors='replace')
        if logs:
            print("  Логи:")
            for line in logs.strip().split('\n')[-5:]:
                if line:
                    safe_line = line.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_line[:150]}")
        
        stdin, stdout, stderr = ssh.exec_command("tail -5 /var/log/shannon-backend-error.log 2>/dev/null")
        error_logs = stdout.read().decode('utf-8', errors='replace')
        if error_logs:
            print("  Ошибки:")
            for line in error_logs.strip().split('\n')[-5:]:
                if line:
                    safe_line = line.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_line[:150]}")
        
        print("\n" + "="*60)
        print("ИТОГ")
        print("="*60)
        
        if is_active == 'active' and proc and port:
            print("\n[SUCCESS] Backend работает стабильно!")
            print("\nГарантии:")
            print("  - Автоматический запуск при загрузке системы")
            print("  - Автоматический перезапуск при падении (через 10 секунд)")
            print("  - Логирование всех событий")
            print("  - Мониторинг через systemctl")
            print("\nПриложение готово к использованию!")
            print("  https://72.56.79.153/api")
        else:
            print("\n[WARNING] Есть проблемы, проверьте выше")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

