#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка ошибки создания сервиса
"""

import paramiko
import requests
import sys
import json

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "https://72.56.79.153"
SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

# Отключаем предупреждения о SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ssh_exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    print("="*70)
    print("ПРОВЕРКА ОШИБКИ СОЗДАНИЯ СЕРВИСА")
    print("="*70)
    
    # 1. Проверяем логи Laravel
    print("\n1. ПРОВЕРКА ЛОГОВ LARAVEL:")
    print("-" * 70)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Получаем последние ошибки из логов
        success, logs, error = ssh_exec(ssh, "tail -100 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -A 20 'services\\|Service\\|500\\|Exception' | tail -50")
        print(logs)
        
        # Проверяем последние строки логов
        print("\n2. ПОСЛЕДНИЕ СТРОКИ ЛОГОВ:")
        print("-" * 70)
        success2, recent_logs, error2 = ssh_exec(ssh, "tail -50 /root/shannon/backend-laravel/storage/logs/laravel.log")
        print(recent_logs)
        
        # Проверяем структуру таблицы services
        print("\n3. ПРОВЕРКА СТРУКТУРЫ ТАБЛИЦЫ SERVICES:")
        print("-" * 70)
        success3, table_structure, error3 = ssh_exec(ssh, "cd /root/shannon/backend-laravel && php artisan tinker --execute=\"echo json_encode(DB::select('PRAGMA table_info(services)'));\" 2>&1 | tail -20")
        print(table_structure)
        
        # Проверяем миграции
        print("\n4. ПРОВЕРКА МИГРАЦИЙ:")
        print("-" * 70)
        success4, migrations, error4 = ssh_exec(ssh, "cd /root/shannon/backend-laravel && php artisan migrate:status 2>&1")
        print(migrations)
        
        # Пробуем создать сервис через API напрямую
        print("\n5. ТЕСТИРОВАНИЕ СОЗДАНИЯ СЕРВИСА:")
        print("-" * 70)
        try:
            # Логинимся
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": "admin", "password": "admin"},
                verify=False,
                timeout=5
            )
            
            if login_response.status_code == 200:
                token = login_response.json()['token']
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                # Пробуем создать сервис
                create_response = requests.post(
                    f"{BASE_URL}/api/services",
                    json={"name": "Test Service", "url": "https://example.com"},
                    headers=headers,
                    verify=False,
                    timeout=5
                )
                
                print(f"  Статус: {create_response.status_code}")
                print(f"  Ответ: {create_response.text[:500]}")
                
                if create_response.status_code != 201:
                    print(f"  ✗ Ошибка создания сервиса")
                else:
                    print(f"  ✓ Сервис создан успешно")
            else:
                print(f"  ✗ Ошибка авторизации: {login_response.status_code}")
        except Exception as e:
            print(f"  ✗ Ошибка тестирования: {str(e)}")
        
        # Проверяем контроллер ServiceController
        print("\n6. ПРОВЕРКА КОНТРОЛЛЕРА:")
        print("-" * 70)
        success5, controller_content, error5 = ssh_exec(ssh, "cat /root/shannon/backend-laravel/app/Http/Controllers/Api/ServiceController.php")
        print(controller_content[:500])
        
        # Проверяем CreateServiceAction
        print("\n7. ПРОВЕРКА CREATE SERVICE ACTION:")
        print("-" * 70)
        success6, action_content, error6 = ssh_exec(ssh, "cat /root/shannon/backend-laravel/app/Domain/Services/Actions/CreateServiceAction.php")
        print(action_content)
        
    finally:
        ssh.close()
    
    print("\n" + "="*70)
    print("РЕКОМЕНДАЦИИ")
    print("="*70)
    print("Проверьте логи выше для определения причины ошибки 500.")
    print("="*70)

if __name__ == "__main__":
    main()


