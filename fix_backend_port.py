#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление проблемы с портом 8000
"""

import paramiko
import sys
import time

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
BACKEND_DIR = "/root/shannon/backend-laravel"

def ssh_exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    print("="*60)
    print("ИСПРАВЛЕНИЕ ПРОБЛЕМЫ С ПОРТОМ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Находим процесс на порту 8000
        print("\n1. ПОИСК ПРОЦЕССА НА ПОРТУ 8000:")
        success, output, error = ssh_exec(ssh, "lsof -i :8000 2>&1 | grep LISTEN || echo 'free'")
        if "LISTEN" in output:
            print(f"  Найден процесс: {output}")
            # Извлекаем PID
            for line in output.split('\n'):
                if 'LISTEN' in line:
                    parts = line.split()
                    if len(parts) > 1:
                        pid = parts[1]
                        print(f"  Останавливаем процесс {pid}...")
                        ssh_exec(ssh, f"kill -9 {pid} 2>&1")
        else:
            print("  Порт свободен")
        
        # 2. Останавливаем старые сервисы
        print("\n2. ОСТАНОВКА СТАРЫХ СЕРВИСОВ:")
        ssh_exec(ssh, "systemctl stop shannon-backend.service 2>&1 || echo 'not found'")
        ssh_exec(ssh, "systemctl stop shannon-laravel.service 2>&1")
        ssh_exec(ssh, "pkill -f 'uvicorn.*8000' 2>&1 || echo 'no uvicorn'")
        ssh_exec(ssh, "pkill -f 'python.*main.py' 2>&1 || echo 'no python'")
        
        # 3. Очистка порта
        print("\n3. ОЧИСТКА ПОРТА:")
        time.sleep(2)
        success, output, error = ssh_exec(ssh, "lsof -i :8000 2>&1")
        if "LISTEN" in output:
            print("  [WARNING] Порт все еще занят, принудительная очистка...")
            ssh_exec(ssh, "fuser -k 8000/tcp 2>&1 || echo 'cleared'")
            time.sleep(2)
        
        # 4. Запуск Laravel backend
        print("\n4. ЗАПУСК LARAVEL BACKEND:")
        ssh_exec(ssh, "systemctl start shannon-laravel.service")
        time.sleep(3)
        
        success, output, error = ssh_exec(ssh, "systemctl status shannon-laravel.service --no-pager -l | head -15")
        print(output)
        
        if "active (running)" in output.lower():
            print("  [OK] Backend запущен")
        else:
            print("  [WARNING] Проверьте логи: journalctl -u shannon-laravel.service -f")
        
        # 5. Проверка доступности
        print("\n5. ПРОВЕРКА ДОСТУПНОСТИ:")
        time.sleep(2)
        success, output, error = ssh_exec(ssh, "curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{}'")
        print(f"  Ответ API: {output[:200]}")
        
        success, output, error = ssh_exec(ssh, "curl -s http://localhost:8000/")
        print(f"  Root: {output[:100]}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nПриложение доступно на: http://{SSH_HOST}")
        print(f"Войдите с учетными данными:")
        print(f"  Логин: admin")
        print(f"  Пароль: admin")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
