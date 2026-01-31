#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная проверка и исправление
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
    print("ФИНАЛЬНАЯ ПРОВЕРКА И ИСПРАВЛЕНИЕ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Обновление репозитория
        print("\n1. ОБНОВЛЕНИЕ:")
        ssh_exec(ssh, "cd /root/shannon && git pull")
        
        # 2. Проверка маршрутов
        print("\n2. ПРОВЕРКА МАРШРУТОВ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan route:list 2>&1")
        if "auth/login" in output:
            print("  [OK] Маршруты загружены")
        else:
            print(f"  [ERROR] Проблема с маршрутами: {output[-300:]}")
        
        # 3. Очистка и перезапуск
        print("\n3. ОЧИСТКА И ПЕРЕЗАПУСК:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan optimize:clear 2>&1")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service")
        time.sleep(4)
        
        # 4. Проверка статуса
        success, output, error = ssh_exec(ssh, "systemctl is-active shannon-laravel.service")
        if "active" in output.lower():
            print("  [OK] Сервис активен")
        else:
            print(f"  [ERROR] Статус: {output}")
            ssh_exec(ssh, "journalctl -u shannon-laravel.service -n 20 --no-pager")
        
        # 5. Тест API
        print("\n4. ТЕСТ API:")
        time.sleep(2)
        success, output, error = ssh_exec(ssh, "curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"test\",\"password\":\"test\"}'")
        print(f"  Ответ: {output[:300]}")
        
        # 6. Проверка через внешний IP
        print("\n5. ПРОВЕРКА ЧЕРЕЗ NGINX:")
        success, output, error = ssh_exec(ssh, f"curl -s http://{SSH_HOST}/api/auth/login -X POST -H 'Content-Type: application/json' -d '{{\"username\":\"test\",\"password\":\"test\"}}'")
        if "validation" in output.lower() or "username" in output.lower() or "password" in output.lower():
            print("  [OK] API работает через Nginx!")
        else:
            print(f"  [WARNING] Ответ: {output[:200]}")
        
        # 7. Проверка frontend
        print("\n6. ПРОВЕРКА FRONTEND:")
        success, output, error = ssh_exec(ssh, f"curl -s http://{SSH_HOST}/ | head -5")
        if "<!DOCTYPE html>" in output or "<html" in output.lower():
            print("  [OK] Frontend доступен")
        else:
            print(f"  [WARNING] Ответ: {output[:100]}")
        
        print("\n" + "="*60)
        print("ПРОВЕРКА ЗАВЕРШЕНА")
        print("="*60)
        print(f"\nОткройте в браузере: http://{SSH_HOST}")
        print(f"Войдите с учетными данными:")
        print(f"  Логин: admin")
        print(f"  Пароль: admin")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

