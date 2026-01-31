#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка наличия всех классов на сервере
"""

import paramiko
import sys

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
    print("ПРОВЕРКА КЛАССОВ НА СЕРВЕРЕ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        classes_to_check = [
            "app/Http/Controllers/Controller.php",
            "app/Http/Controllers/Api/AuthController.php",
            "app/Http/Requests/LoginRequest.php",
            "app/Domain/Auth/Actions/LoginAction.php",
            "app/Domain/Auth/Actions/GetCurrentUserAction.php",
            "app/Data/Auth/LoginData.php",
            "app/Data/Auth/UserData.php",
            "app/Models/User.php",
        ]
        
        print("\nПРОВЕРКА ФАЙЛОВ:")
        for class_path in classes_to_check:
            success, output, error = ssh_exec(ssh, f"test -f {BACKEND_DIR}/{class_path} && echo 'EXISTS' || echo 'MISSING'")
            status = output.strip()
            print(f"  {class_path}: {status}")
        
        # Проверка автозагрузки
        print("\nПРОВЕРКА АВТОЗАГРУЗКИ:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan tinker --execute=\"class_exists('App\\\\Http\\\\Controllers\\\\Controller') ? 'OK' : 'FAIL'\" 2>&1")
        print(f"  Controller: {output.strip()}")
        
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan tinker --execute=\"class_exists('App\\\\Http\\\\Requests\\\\LoginRequest') ? 'OK' : 'FAIL'\" 2>&1")
        print(f"  LoginRequest: {output.strip()}")
        
        # Попытка загрузить класс напрямую
        print("\nПРЯМАЯ ПРОВЕРКА:")
        success, output, error = ssh_exec(ssh, f"cd {BACKEND_DIR} && php -r \"require 'vendor/autoload.php'; echo class_exists('App\\\\Http\\\\Controllers\\\\Controller') ? 'OK' : 'FAIL';\" 2>&1")
        print(f"  Controller: {output.strip()}")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

