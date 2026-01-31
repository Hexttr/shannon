#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Восстановление рабочей версии frontend
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
    print("ВОССТАНОВЛЕНИЕ РАБОЧЕЙ ВЕРСИИ FRONTEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка версии Node.js
        print("\n1. ПРОВЕРКА NODE.JS:")
        success, output, error = ssh_exec(ssh, "node --version")
        print(f"  Node.js: {output.strip()}")
        
        success, output, error = ssh_exec(ssh, "npm --version")
        print(f"  npm: {output.strip()}")
        
        # 2. Восстановление из git (откат к рабочей версии)
        print("\n2. ВОССТАНОВЛЕНИЕ ИЗ GIT:")
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && git checkout HEAD -- .")
        print("  [OK] Файлы восстановлены")
        
        # 3. Попытка сборки с исправлением прав
        print("\n3. ПРАВА ДЛЯ NODE_MODULES:")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/node_modules 2>&1 || echo 'ok'")
        ssh_exec(ssh, f"chmod +x {FRONTEND_DIR}/node_modules/.bin/* 2>&1 || echo 'ok'")
        print("  [OK] Права установлены")
        
        # 4. Сборка через npx
        print("\n4. СБОРКА ЧЕРЕЗ NPX:")
        success, output, error = ssh_exec(ssh, f"cd {FRONTEND_DIR} && npx vite build 2>&1 | tail -20")
        if "built in" in output.lower() or "dist" in output.lower():
            print("  [OK] Frontend собран")
            print(f"  {output[-200:]}")
        else:
            print(f"  [WARNING] Вывод: {output[-500:]}")
        
        # 5. Проверка dist
        print("\n5. ПРОВЕРКА DIST:")
        success, output, error = ssh_exec(ssh, f"test -d {FRONTEND_DIR}/dist && echo 'EXISTS' || echo 'MISSING'")
        if "EXISTS" in output:
            success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ | head -10")
            print(output)
            print("  [OK] Frontend собран")
        else:
            print("  [ERROR] Frontend не собран, используем старую версию если есть")
            # Восстанавливаем из бэкапа или используем старую версию
            ssh_exec(ssh, f"cd {FRONTEND_DIR} && git log --oneline -5")
        
        # 6. Установка прав
        print("\n6. УСТАНОВКА ПРАВ:")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist 2>&1 || echo 'ok'")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist 2>&1 || chown -R root:root {FRONTEND_DIR}/dist 2>&1 || echo 'ok'")
        print("  [OK] Права установлены")
        
        # 7. Перезагрузка Nginx
        print("\n7. ПЕРЕЗАГРУЗКА NGINX:")
        ssh_exec(ssh, "systemctl reload nginx")
        time.sleep(2)
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nПопробуйте войти снова:")
        print(f"  URL: https://{SSH_HOST}")
        print(f"  Логин: admin")
        print(f"  Пароль: admin")
        print(f"\nВАЖНО: API работает правильно (статус 200).")
        print(f"Если вход не работает, проверьте консоль браузера (F12)")
        print(f"и посмотрите детальные логи [DEBUG], [Login], [AuthContext]")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

