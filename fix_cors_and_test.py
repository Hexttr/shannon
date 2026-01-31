#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление CORS и тестирование
"""

import paramiko
import sys
import time
import requests
from urllib3.exceptions import InsecureRequestWarning
import urllib3

urllib3.disable_warnings(InsecureRequestWarning)

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
    print("ИСПРАВЛЕНИЕ CORS")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    sftp = ssh.open_sftp()
    
    try:
        # 1. Копирование обновленного файла CORS
        print("\n1. ОБНОВЛЕНИЕ CORS:")
        local_file = "backend-laravel/config/cors.php"
        remote_file = f"{BACKEND_DIR}/config/cors.php"
        
        with open(local_file, 'rb') as f:
            sftp.putfo(f, remote_file)
        print("  [OK] Файл CORS обновлен")
        
        # 2. Очистка кэша
        print("\n2. ОЧИСТКА КЭША:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan config:clear 2>&1")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan config:cache 2>&1")
        print("  [OK] Кэш очищен")
        
        # 3. Перезапуск backend
        print("\n3. ПЕРЕЗАПУСК BACKEND:")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service")
        time.sleep(3)
        
        # 4. Тест с правильными заголовками (как браузер)
        print("\n4. ТЕСТ С ЗАГОЛОВКАМИ БРАУЗЕРА:")
        response = requests.post(
            f"https://{SSH_HOST}/api/auth/login",
            json={"username": "admin", "password": "admin"},
            headers={
                "Content-Type": "application/json",
                "Origin": f"https://{SSH_HOST}",
                "Referer": f"https://{SSH_HOST}/",
            },
            verify=False,
            timeout=10
        )
        
        print(f"  Статус: {response.status_code}")
        print(f"  Заголовки ответа:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower() or 'cors' in key.lower():
                print(f"    {key}: {value}")
        
        if response.status_code == 200:
            print("  ✅ Запрос успешен!")
            print(f"  Ответ: {response.text[:200]}")
        else:
            print(f"  ❌ Ошибка: {response.text[:300]}")
        
        # 5. Проверка OPTIONS запроса (preflight)
        print("\n5. ТЕСТ PREFLIGHT (OPTIONS):")
        response = requests.options(
            f"https://{SSH_HOST}/api/auth/login",
            headers={
                "Origin": f"https://{SSH_HOST}",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
            verify=False,
            timeout=10
        )
        
        print(f"  Статус: {response.status_code}")
        print(f"  Заголовки:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower():
                print(f"    {key}: {value}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nПопробуйте войти снова:")
        print(f"  URL: https://{SSH_HOST}")
        print(f"  Логин: admin")
        print(f"  Пароль: admin")
        
    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    main()

