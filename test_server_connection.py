#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки подключения к серверу через SSH (paramiko)
"""

import paramiko
import sys
import os

# Настройка кодировки для Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

# Данные сервера
SERVER_HOST = "72.56.79.153"
SERVER_USER = "root"
SERVER_PASSWORD = "m8J@2_6whwza6U"
SERVER_PORT = 22

def test_connection():
    """Тестирует SSH подключение к серверу"""
    print(f"Подключение к серверу {SERVER_HOST}...")
    
    try:
        # Создание SSH клиента
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Подключение
        print(f"Попытка подключения как {SERVER_USER}...")
        ssh.connect(
            hostname=SERVER_HOST,
            port=SERVER_PORT,
            username=SERVER_USER,
            password=SERVER_PASSWORD,
            timeout=10
        )
        
        print("[OK] Подключение успешно!")
        
        # Выполнение тестовой команды
        print("\nВыполнение тестовой команды...")
        stdin, stdout, stderr = ssh.exec_command("uname -a && pwd && ls -la /root/shannon 2>/dev/null | head -5")
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if output:
            print("Результат:")
            print(output)
        
        if error:
            print("Ошибки:")
            print(error)
        
        # Проверка статуса сервисов
        print("\nПроверка статуса сервисов...")
        stdin, stdout, stderr = ssh.exec_command("systemctl status shannon-laravel.service --no-pager | head -10")
        service_status = stdout.read().decode('utf-8')
        if service_status:
            print(service_status)
        
        # Проверка Nginx
        print("\nПроверка Nginx...")
        stdin, stdout, stderr = ssh.exec_command("systemctl status nginx --no-pager | head -5")
        nginx_status = stdout.read().decode('utf-8')
        if nginx_status:
            print(nginx_status)
        
        ssh.close()
        print("\n[OK] Все проверки пройдены успешно!")
        return True
        
    except paramiko.AuthenticationException:
        print("[ERROR] Ошибка аутентификации. Проверьте логин и пароль.")
        return False
    except paramiko.SSHException as e:
        print(f"[ERROR] Ошибка SSH: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

