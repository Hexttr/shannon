#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Принудительная пересборка frontend
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
    print("ПРИНУДИТЕЛЬНАЯ ПЕРЕСБОРКА FRONTEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Обновление репозитория
        print("\n1. ОБНОВЛЕНИЕ РЕПОЗИТОРИЯ:")
        ssh_exec(ssh, "cd /root/shannon && git pull")
        print("  [OK] Репозиторий обновлен")
        
        # 2. Удаление старого dist
        print("\n2. УДАЛЕНИЕ СТАРОГО DIST:")
        ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/dist")
        print("  [OK] Старый dist удален")
        
        # 3. Проверка .env
        print("\n3. ПРОВЕРКА .ENV:")
        success, output, error = ssh_exec(ssh, f"cat {FRONTEND_DIR}/.env")
        print(output)
        
        # 4. Пересборка
        print("\n4. ПЕРЕСБОРКА:")
        print("  Это может занять несколько минут...")
        # Запускаем сборку в фоне и ждем
        ssh.exec_command(f"cd {FRONTEND_DIR} && /usr/bin/npm run build > /tmp/frontend_build.log 2>&1 &")
        time.sleep(30)  # Ждем 30 секунд
        
        # Проверяем процесс
        success, output, error = ssh_exec(ssh, "ps aux | grep 'npm run build' | grep -v grep")
        if output:
            print("  Сборка еще идет, ждем еще...")
            time.sleep(30)
        
        # Проверяем лог
        success, output, error = ssh_exec(ssh, "tail -50 /tmp/frontend_build.log")
        print(output[-500:])
        
        # 5. Проверка dist
        print("\n5. ПРОВЕРКА DIST:")
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ 2>&1 | head -10")
        print(output)
        
        if "index.html" in output:
            print("  [OK] Frontend собран")
        else:
            print("  [ERROR] Frontend не собран")
            return
        
        # 6. Установка прав
        print("\n6. УСТАНОВКА ПРАВ:")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist 2>&1 || chown -R root:root {FRONTEND_DIR}/dist")
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
        print(f"\nОткройте консоль браузера (F12) и проверьте:")
        print(f"  1. Логи [DEBUG] при загрузке страницы")
        print(f"  2. Логи [Login] при попытке входа")
        print(f"  3. Логи [AuthContext] при обработке ответа")
        print(f"  4. Network tab - статус запроса /api/auth/login")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

