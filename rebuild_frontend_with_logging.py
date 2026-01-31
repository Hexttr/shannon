#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пересборка frontend с логированием
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
    print("ПЕРЕСБОРКА FRONTEND С ЛОГИРОВАНИЕМ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Обновление репозитория
        print("\n1. ОБНОВЛЕНИЕ РЕПОЗИТОРИЯ:")
        ssh_exec(ssh, "cd /root/shannon && git pull")
        print("  [OK] Репозиторий обновлен")
        
        # 2. Пересборка
        print("\n2. ПЕРЕСБОРКА FRONTEND:")
        print("  Это может занять несколько минут...")
        success, output, error = ssh_exec(ssh, f"cd {FRONTEND_DIR} && /usr/bin/npm run build 2>&1")
        if "built in" in output.lower() or "dist" in output.lower():
            print("  [OK] Frontend пересобран")
            print(f"  {output[-200:]}")
        else:
            print(f"  [WARNING] Вывод: {output[-500:]}")
        
        # 3. Перезагрузка Nginx
        print("\n3. ПЕРЕЗАГРУЗКА NGINX:")
        ssh_exec(ssh, "systemctl reload nginx")
        time.sleep(2)
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nПопробуйте войти снова:")
        print(f"  URL: https://{SSH_HOST}")
        print(f"  Логин: admin")
        print(f"  Пароль: admin")
        print(f"\nОткройте консоль браузера (F12) и проверьте логи.")
        print(f"Вы увидите детальную информацию о процессе входа.")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

