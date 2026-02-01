#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка Network Error - диагностика API
"""

import paramiko
import requests
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "https://72.56.79.153"

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
    print("ДИАГНОСТИКА NETWORK ERROR")
    print("="*70)
    
    # 1. Проверка API через HTTPS
    print("\n1. ПРОВЕРКА API ЧЕРЕЗ HTTPS:")
    print("-" * 70)
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            verify=False,
            timeout=5
        )
        print(f"  URL: {BASE_URL}/api/auth/login")
        print(f"  Статус: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ API доступен через HTTPS")
            data = response.json()
            print(f"  Ответ: {data.get('user', {}).get('username', 'не найден')}")
        else:
            print(f"  ✗ API вернул ошибку: {response.status_code}")
            print(f"  Ответ: {response.text[:200]}")
    except requests.exceptions.SSLError as e:
        print(f"  ✗ SSL ошибка: {str(e)}")
    except requests.exceptions.ConnectionError as e:
        print(f"  ✗ Ошибка подключения: {str(e)}")
    except Exception as e:
        print(f"  ✗ Ошибка: {str(e)}")
    
    # 2. Проверка backend на порту 8000
    print("\n2. ПРОВЕРКА BACKEND НА ПОРТУ 8000:")
    print("-" * 70)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("72.56.79.153", username="root", password="m8J@2_6whwza6U", timeout=30)
    
    try:
        # Проверяем, слушает ли что-то порт 8000
        success, output, error = ssh_exec(ssh, "netstat -tlnp | grep :8000 || ss -tlnp | grep :8000")
        if ':8000' in output:
            print(f"  ✓ Порт 8000 занят:")
            print(f"    {output}")
        else:
            print(f"  ✗ Порт 8000 НЕ занят - backend не работает!")
        
        # Проверяем статус Laravel backend service
        print("\n3. ПРОВЕРКА СТАТУСА BACKEND SERVICE:")
        print("-" * 70)
        success2, status, error2 = ssh_exec(ssh, "systemctl status shannon-backend --no-pager 2>&1 | head -15")
        print(status)
        
        # Проверяем доступность backend локально
        print("\n4. ПРОВЕРКА BACKEND ЛОКАЛЬНО:")
        print("-" * 70)
        success3, local_test, error3 = ssh_exec(ssh, "curl -s http://127.0.0.1:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' | head -5")
        if 'user' in local_test or 'token' in local_test:
            print(f"  ✓ Backend отвечает локально")
            print(f"    Ответ: {local_test[:200]}")
        else:
            print(f"  ✗ Backend не отвечает локально")
            print(f"    Ответ: {local_test[:200]}")
        
        # Проверяем конфигурацию Nginx для /api
        print("\n5. ПРОВЕРКА КОНФИГУРАЦИИ NGINX ДЛЯ /API:")
        print("-" * 70)
        success4, nginx_config, error4 = ssh_exec(ssh, "grep -A 10 'location /api' /etc/nginx/sites-available/pentest")
        print(nginx_config)
        
        # Проверяем логи Nginx
        print("\n6. ПРОВЕРКА ЛОГОВ NGINX:")
        print("-" * 70)
        success5, nginx_logs, error5 = ssh_exec(ssh, "tail -20 /var/log/nginx/error.log | grep -i 'api\\|8000\\|proxy' || tail -5 /var/log/nginx/error.log")
        print(nginx_logs)
        
        # Проверяем логи Laravel
        print("\n7. ПРОВЕРКА ЛОГОВ LARAVEL:")
        print("-" * 70)
        success6, laravel_logs, error6 = ssh_exec(ssh, "tail -30 /root/shannon/backend-laravel/storage/logs/laravel.log 2>&1 | tail -20")
        if 'No such file' not in laravel_logs:
            print(laravel_logs)
        else:
            print("  Файл логов не найден или пуст")
        
    finally:
        ssh.close()
    
    # Итоги и рекомендации
    print("\n" + "="*70)
    print("РЕКОМЕНДАЦИИ")
    print("="*70)
    print("Если backend не работает:")
    print("1. Запустите backend: systemctl start shannon-backend")
    print("2. Проверьте статус: systemctl status shannon-backend")
    print("3. Проверьте логи: journalctl -u shannon-backend -n 50")
    print("\nЕсли backend работает, но API недоступен:")
    print("1. Проверьте конфигурацию Nginx для /api")
    print("2. Проверьте, что proxy_pass указывает на http://127.0.0.1:8000")
    print("3. Перезагрузите Nginx: systemctl reload nginx")
    print("="*70)

if __name__ == "__main__":
    main()



