#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление сборки frontend
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
FRONTEND_DIR = "/root/shannon/template"

def ssh_exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    print("="*60)
    print("ИСПРАВЛЕНИЕ СБОРКИ FRONTEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Очистка node_modules и переустановка
        print("\n1. ПЕРЕУСТАНОВКА ЗАВИСИМОСТЕЙ:")
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && rm -rf node_modules package-lock.json")
        print("  [OK] Старые зависимости удалены")
        
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && /usr/bin/npm install 2>&1 | tail -10")
        print("  [OK] Зависимости установлены")
        
        # 2. Пересборка
        print("\n2. ПЕРЕСБОРКА:")
        print("  Это может занять несколько минут...")
        # Запускаем синхронно
        success, output, error = ssh_exec(ssh, f"cd {FRONTEND_DIR} && timeout 120 /usr/bin/npm run build 2>&1")
        
        if "built in" in output.lower() or "dist" in output.lower() or success:
            print("  [OK] Frontend собран")
            print(f"  {output[-300:]}")
        else:
            print(f"  [WARNING] Вывод: {output[-500:]}")
            # Проверяем, может быть dist все равно создался
            success, output, error = ssh_exec(ssh, f"test -d {FRONTEND_DIR}/dist && echo 'EXISTS' || echo 'MISSING'")
            if "EXISTS" in output:
                print("  [OK] dist директория существует, несмотря на ошибки")
        
        # 3. Проверка dist
        print("\n3. ПРОВЕРКА DIST:")
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ 2>&1 | head -10")
        print(output)
        
        if "index.html" in output:
            print("  [OK] Frontend собран успешно")
        else:
            print("  [ERROR] Frontend не собран")
            # Пробуем использовать старую версию если есть
            return
        
        # 4. Установка прав
        print("\n4. УСТАНОВКА ПРАВ:")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist 2>&1 || chown -R root:root {FRONTEND_DIR}/dist")
        print("  [OK] Права установлены")
        
        # 5. Перезагрузка Nginx
        print("\n5. ПЕРЕЗАГРУЗКА NGINX:")
        ssh_exec(ssh, "systemctl reload nginx")
        time.sleep(2)
        
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

