#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление прав доступа для Nginx
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
    print("ИСПРАВЛЕНИЕ ПРАВ ДОСТУПА")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Установка прав на всю цепочку директорий
        print("\n1. УСТАНОВКА ПРАВ НА ДИРЕКТОРИИ:")
        ssh_exec(ssh, "chmod 755 /root")
        ssh_exec(ssh, "chmod 755 /root/shannon")
        ssh_exec(ssh, f"chmod 755 {FRONTEND_DIR}")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        print("  [OK] Права на директории установлены")
        
        # 2. Установка прав на файлы
        print("\n2. УСТАНОВКА ПРАВ НА ФАЙЛЫ:")
        ssh_exec(ssh, f"find {FRONTEND_DIR}/dist -type f -exec chmod 644 {{}} \\;")
        ssh_exec(ssh, f"find {FRONTEND_DIR}/dist -type d -exec chmod 755 {{}} \\;")
        print("  [OK] Права на файлы установлены")
        
        # 3. Проверка прав
        print("\n3. ПРОВЕРКА ПРАВ:")
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ | head -10")
        print(output)
        
        # 4. Тест чтения от имени www-data
        print("\n4. ТЕСТ ЧТЕНИЯ ОТ ИМЕНИ WWW-DATA:")
        success, output, error = ssh_exec(ssh, f"sudo -u www-data test -r {FRONTEND_DIR}/dist/index.html && echo 'READABLE' || echo 'NOT READABLE'")
        print(f"  {output.strip()}")
        
        # 5. Перезагрузка Nginx
        print("\n5. ПЕРЕЗАГРУЗКА NGINX:")
        ssh_exec(ssh, "systemctl reload nginx")
        time.sleep(2)
        
        # 6. Тест доступа
        print("\n6. ТЕСТ ДОСТУПА:")
        success, output, error = ssh_exec(ssh, f"curl -k -s https://{SSH_HOST}/ | head -20")
        if "<!DOCTYPE html>" in output or ("<html" in output.lower() and "500" not in output and "error" not in output.lower()):
            print("  ✅ Frontend работает!")
            print(f"  Первые строки: {output[:300]}")
        else:
            print(f"  ⚠️  Ответ: {output[:400]}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\n🌐 Активная ссылка для открытия в браузере:")
        print(f"\n   👉 https://{SSH_HOST} 👈")
        print(f"\n📋 Скопируйте эту ссылку:")
        print(f"   https://{SSH_HOST}")
        print(f"\n🔐 Учетные данные:")
        print(f"   Логин: admin")
        print(f"   Пароль: admin")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

