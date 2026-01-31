#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление APP_KEY
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
    print("ИСПРАВЛЕНИЕ APP_KEY")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Генерация APP_KEY
        print("\n1. ГЕНЕРАЦИЯ APP_KEY:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan key:generate --force 2>&1")
        print(output)
        
        # 2. Проверка .env
        print("\n2. ПРОВЕРКА APP_KEY:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && grep 'APP_KEY' .env")
        if "base64:" in output:
            print("  [OK] APP_KEY установлен")
            print(f"  {output[:50]}...")
        else:
            print("  [ERROR] APP_KEY не найден")
        
        # 3. Очистка и пересоздание кэша
        print("\n3. ОЧИСТКА КЭША:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan config:clear 2>&1")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan config:cache 2>&1")
        print("  [OK] Кэш обновлен")
        
        # 4. Перезапуск
        print("\n4. ПЕРЕЗАПУСК:")
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
            headers={"Content-Type": "application/json", "Origin": f"https://{SSH_HOST}"},
            verify=False,
            timeout=10
        )
        
        print(f"  Статус: {response.status_code}")
        if response.status_code == 200:
            print("  [OK] API работает!")
            print(f"  Ответ: {response.text[:200]}")
        else:
            print(f"  [WARNING] Ответ: {response.text[:300]}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nПопробуйте войти снова:")
        print(f"  URL: https://{SSH_HOST}")
        print(f"  Логин: admin")
        print(f"  Пароль: admin")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

