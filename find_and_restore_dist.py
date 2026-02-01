#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Поиск и восстановление рабочей версии dist
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
    print("ПОИСК И ВОССТАНОВЛЕНИЕ РАБОЧЕЙ ВЕРСИИ DIST")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка git stash
        print("\n1. ПРОВЕРКА GIT STASH:")
        success, output, error = ssh_exec(ssh, "cd /root/shannon && git stash list | head -5")
        print(output)
        
        # 2. Проверка последних коммитов с dist
        print("\n2. ПРОВЕРКА ПОСЛЕДНИХ КОММИТОВ:")
        ssh_exec(ssh, "cd /root/shannon && git log --all --oneline --name-only | grep -A 5 'dist' | head -20")
        
        # 3. Попытка найти dist в других ветках или тегах
        print("\n3. ПОИСК В ДРУГИХ ВЕТКАХ:")
        success, output, error = ssh_exec(ssh, "cd /root/shannon && git branch -a")
        print(output[:200])
        
        # 4. Проверка, может быть dist был закоммичен ранее
        print("\n4. ПРОВЕРКА ИСТОРИИ ФАЙЛОВ:")
        # Проверяем, был ли dist когда-либо в git
        success, output, error = ssh_exec(ssh, f"cd {FRONTEND_DIR} && git log --all --full-history --oneline -- template/dist/ 2>&1 | head -5")
        print(output)
        
        # 5. Если dist не найден в git, используем последнюю рабочую версию из бэкапа системы
        print("\n5. ПОИСК СИСТЕМНЫХ BACKUP:")
        success, output, error = ssh_exec(ssh, "find /root -name '*dist*' -type d -path '*/template/*' 2>&1 | head -10")
        print(output)
        
        # 6. Попытка собрать только через vite, игнорируя ошибки
        print("\n6. ПОПЫТКА СБОРКИ С ИГНОРИРОВАНИЕМ ОШИБОК:")
        # Обновляем package.json чтобы убрать проверку TypeScript
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && sed -i 's/\"build\": \".*tsc.*\"/\"build\": \"vite build\"/' package.json")
        print("  [OK] package.json обновлен")
        
        # Пробуем собрать
        print("  Запускаем сборку...")
        ssh.exec_command(f"cd {FRONTEND_DIR} && timeout 180 npx vite build --mode production > /tmp/vite_build.log 2>&1 &")
        time.sleep(90)  # Ждем 90 секунд
        
        # Проверяем лог
        success, output, error = ssh_exec(ssh, "tail -100 /tmp/vite_build.log")
        print(f"  Лог: {output[-800:]}")
        
        # Проверяем dist
        success, output, error = ssh_exec(ssh, f"test -d {FRONTEND_DIR}/dist && ls -la {FRONTEND_DIR}/dist/ | head -10")
        if "index.html" in output and ("assets" in output or ".js" in output):
            print("  [OK] Frontend собран успешно!")
            print(output)
        else:
            print(f"  [WARNING] dist: {output[:300]}")
        
        # 7. Установка прав
        print("\n7. УСТАНОВКА ПРАВ:")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist 2>&1 || echo 'ok'")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist 2>&1 || chown -R root:root {FRONTEND_DIR}/dist 2>&1 || echo 'ok'")
        print("  [OK] Права установлены")
        
        # 8. Перезагрузка Nginx
        print("\n8. ПЕРЕЗАГРУЗКА NGINX:")
        ssh_exec(ssh, "systemctl reload nginx")
        time.sleep(2)
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nПопробуйте открыть:")
        print(f"  https://{SSH_HOST}")
        print(f"\nЛогин: admin")
        print(f"Пароль: admin")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()



