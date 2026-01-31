#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление конфигурации Sanctum
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
    print("ИСПРАВЛЕНИЕ КОНФИГУРАЦИИ SANCTUM")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Обновление .env для Sanctum
        print("\n1. ОБНОВЛЕНИЕ .ENV:")
        # Добавляем домен в SANCTUM_STATEFUL_DOMAINS
        ssh_exec(ssh, f"cd {BACKEND_DIR} && grep -q 'SANCTUM_STATEFUL_DOMAINS' .env || echo 'SANCTUM_STATEFUL_DOMAINS=72.56.79.153,localhost,localhost:3000,localhost:8000,127.0.0.1,127.0.0.1:8000,::1' >> .env")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && sed -i 's|SANCTUM_STATEFUL_DOMAINS=.*|SANCTUM_STATEFUL_DOMAINS=72.56.79.153,localhost,localhost:3000,localhost:8000,127.0.0.1,127.0.0.1:8000,::1|' .env")
        print("  [OK] SANCTUM_STATEFUL_DOMAINS обновлен")
        
        # 2. Проверка текущего .env
        print("\n2. ПРОВЕРКА .ENV:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && grep -E '^(SANCTUM_STATEFUL_DOMAINS|APP_URL|FRONTEND_URL)' .env")
        print(output)
        
        # 3. Обновление конфигурации Sanctum
        print("\n3. ОБНОВЛЕНИЕ КОНФИГУРАЦИИ SANCTUM:")
        # Обновляем config/sanctum.php чтобы включить наш домен
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan config:clear 2>&1")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan config:cache 2>&1")
        print("  [OK] Конфигурация обновлена")
        
        # 4. Перезапуск backend
        print("\n4. ПЕРЕЗАПУСК BACKEND:")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service")
        time.sleep(3)
        
        # 5. Тест
        print("\n5. ТЕСТ:")
        import requests
        from urllib3.exceptions import InsecureRequestWarning
        import urllib3
        urllib3.disable_warnings(InsecureRequestWarning)
        
        response = requests.post(
            f"https://{SSH_HOST}/api/auth/login",
            json={"username": "admin", "password": "admin"},
            headers={
                "Content-Type": "application/json",
                "Origin": f"https://{SSH_HOST}",
                "Referer": f"https://{SSH_HOST}/",
                "Accept": "application/json",
            },
            verify=False,
            timeout=10
        )
        
        print(f"  Статус: {response.status_code}")
        if response.status_code == 200:
            print("  [OK] API работает!")
        else:
            print(f"  [WARNING] Ответ: {response.text[:300]}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nПопробуйте войти снова:")
        print(f"  URL: https://{SSH_HOST}")
        print(f"  Логин: admin")
        print(f"  Пароль: admin")
        print(f"\nЕсли проблема сохраняется:")
        print(f"  1. Очистите кэш браузера (Ctrl+Shift+Delete)")
        print(f"  2. Откройте консоль (F12) и проверьте ошибки")
        print(f"  3. Проверьте Network tab - какой статус у запроса /api/auth/login")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

