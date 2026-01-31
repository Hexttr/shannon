#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка запроса из браузера
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
    print("ПРОВЕРКА ЗАПРОСОВ ИЗ БРАУЗЕРА")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Очистка логов
        print("\n1. ОЧИСТКА ЛОГОВ:")
        ssh_exec(ssh, f"echo '' > {BACKEND_DIR}/storage/logs/laravel.log")
        print("  [OK] Логи очищены")
        print("\n  Теперь попробуйте войти в браузере и нажмите Enter...")
        input()
        
        # Чтение логов
        print("\n2. ЛОГИ LARAVEL:")
        success, output, error = ssh_exec(ssh, f"tail -100 {BACKEND_DIR}/storage/logs/laravel.log")
        print(output[-2000:])
        
        # Проверка валидации
        print("\n3. ПРОВЕРКА ВАЛИДАЦИИ:")
        if "validation" in output.lower() or "422" in output.lower():
            print("  Обнаружена ошибка валидации")
            # Извлекаем детали валидации
            import re
            validation_match = re.search(r'validation.*?errors.*?\{.*?\}', output, re.DOTALL | re.IGNORECASE)
            if validation_match:
                print(f"  Детали: {validation_match.group()[:500]}")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

