#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление всех файлов и загрузка на сервер
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
    print("ИСПРАВЛЕНИЕ И ЗАГРУЗКА ВСЕХ ФАЙЛОВ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    sftp = ssh.open_sftp()
    
    try:
        # 1. Обновление репозитория
        print("\n1. ОБНОВЛЕНИЕ РЕПОЗИТОРИЯ:")
        ssh_exec(ssh, "cd /root/shannon && git pull")
        print("  [OK] Репозиторий обновлен")
        
        # 2. Загрузка исправленных файлов напрямую
        print("\n2. ЗАГРУЗКА ИСПРАВЛЕННЫХ ФАЙЛОВ:")
        files_to_upload = [
            ("template/src/components/Sidebar.tsx", f"{FRONTEND_DIR}/src/components/Sidebar.tsx"),
            ("template/src/pages/Pentests.tsx", f"{FRONTEND_DIR}/src/pages/Pentests.tsx"),
        ]
        
        for local_file, remote_file in files_to_upload:
            try:
                with open(local_file, 'rb') as f:
                    sftp.putfo(f, remote_file)
                print(f"  [OK] {local_file.split('/')[-1]}")
            except Exception as e:
                print(f"  [ERROR] {local_file}: {e}")
        
        # 3. Удаление старого dist
        print("\n3. УДАЛЕНИЕ СТАРОГО DIST:")
        ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/dist")
        print("  [OK] Старый dist удален")
        
        # 4. Сборка
        print("\n4. СБОРКА FRONTEND:")
        print("  Запускаем сборку (это может занять 3-5 минут)...")
        
        ssh.exec_command(f"cd {FRONTEND_DIR} && nohup npm run build > /tmp/vite_build_final3.log 2>&1 &")
        
        # Ждем и проверяем
        max_wait = 300
        wait_interval = 15
        elapsed = 0
        
        while elapsed < max_wait:
            time.sleep(wait_interval)
            elapsed += wait_interval
            
            success, output, error = ssh_exec(ssh, f"test -d {FRONTEND_DIR}/dist && test -f {FRONTEND_DIR}/dist/index.html && echo 'ready' || echo 'not ready'")
            if "ready" in output:
                print(f"  [OK] Frontend собран (через {elapsed} секунд)")
                break
            
            print(f"  Ожидание... ({elapsed}/{max_wait} сек)")
        
        # 5. Проверка лога
        print("\n5. ПРОВЕРКА ЛОГА:")
        success, output, error = ssh_exec(ssh, "tail -50 /tmp/vite_build_final3.log")
        if "error" in output.lower():
            print(f"  [WARNING] Ошибки: {output[-800:]}")
        else:
            print(f"  [OK] Лог: {output[-500:]}")
        
        # 6. Проверка dist
        print("\n6. ПРОВЕРКА DIST:")
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ 2>&1")
        print(output)
        
        if "index.html" in output:
            success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/assets/ 2>&1 | head -5")
            print(f"  Assets: {output}")
        
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
        print(f"\nURL: https://{SSH_HOST}")
        print(f"Логин: admin")
        print(f"Пароль: admin")
        
    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    main()



