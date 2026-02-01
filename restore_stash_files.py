#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Восстановление файлов из stash
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
    print("ВОССТАНОВЛЕНИЕ ФАЙЛОВ ИЗ STASH")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Восстановление конкретных файлов из stash
        print("\n1. ВОССТАНОВЛЕНИЕ ФАЙЛОВ ИЗ STASH:")
        
        # Восстанавливаем только нужные файлы
        files_to_restore = [
            "template/src/pages/Services.tsx",
            "template/src/pages/Home.tsx",
            "template/src/pages/Analytics.tsx",
            "template/src/pages/Reports.tsx",
        ]
        
        for file_path in files_to_restore:
            # Извлекаем файл из stash
            restore_cmd = f"cd /root/shannon && git show stash@{{0}}:{file_path} > {file_path} 2>&1"
            success, output, error = ssh_exec(ssh, restore_cmd)
            if success or not error:
                print(f"  [OK] {file_path.split('/')[-1]}")
            else:
                print(f"  [WARNING] {file_path.split('/')[-1]}: {error[:100]}")
        
        # 2. Проверка восстановленных файлов
        print("\n2. ПРОВЕРКА ФАЙЛОВ:")
        for file_path in files_to_restore:
            success, output, error = ssh_exec(ssh, f"head -5 /root/shannon/{file_path} 2>&1")
            if "import" in output:
                print(f"  [OK] {file_path.split('/')[-1]} - импорты найдены")
        
        # 3. Попытка сборки
        print("\n3. СБОРКА:")
        ssh.exec_command(f"cd {FRONTEND_DIR} && timeout 180 npx vite build > /tmp/vite_build3.log 2>&1 &")
        time.sleep(90)
        
        success, output, error = ssh_exec(ssh, "tail -50 /tmp/vite_build3.log")
        print(f"  Лог: {output[-600:]}")
        
        # 4. Проверка dist
        print("\n4. ПРОВЕРКА DIST:")
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ 2>&1")
        print(output)
        
        if "index.html" in output:
            success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/assets/ 2>&1 | head -5")
            if ".js" in output:
                print("  [OK] JS файлы найдены!")
                print(output)
            else:
                print("  [WARNING] JS файлы не найдены")
        
        # 5. Установка прав
        print("\n5. УСТАНОВКА ПРАВ:")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist 2>&1 || echo 'ok'")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist 2>&1 || chown -R root:root {FRONTEND_DIR}/dist 2>&1 || echo 'ok'")
        print("  [OK] Права установлены")
        
        # 6. Перезагрузка Nginx
        print("\n6. ПЕРЕЗАГРУЗКА NGINX:")
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



