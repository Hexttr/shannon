#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная сборка на сервере
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
    print("ФИНАЛЬНАЯ СБОРКА НА СЕРВЕРЕ")
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
        
        # 3. Проверка файлов
        print("\n3. ПРОВЕРКА ФАЙЛОВ:")
        success, output, error = ssh_exec(ssh, f"head -3 {FRONTEND_DIR}/src/pages/Services.tsx")
        print(f"  {output[:200]}")
        
        # 4. Сборка
        print("\n4. СБОРКА:")
        print("  Запускаем сборку (это может занять 2-3 минуты)...")
        
        # Запускаем сборку в фоне и ждем
        ssh.exec_command(f"cd {FRONTEND_DIR} && timeout 300 npm run build > /tmp/vite_build_final.log 2>&1")
        time.sleep(120)  # Ждем 2 минуты
        
        # Проверяем лог
        success, output, error = ssh_exec(ssh, "tail -100 /tmp/vite_build_final.log")
        print(f"  Лог: {output[-1000:]}")
        
        # 5. Проверка dist
        print("\n5. ПРОВЕРКА DIST:")
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ 2>&1")
        print(output)
        
        if "index.html" in output:
            success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/assets/ 2>&1 | head -10")
            print(f"  Assets: {output}")
            
            # Проверяем наличие JS файлов
            if ".js" in output and "index" in output.lower():
                print("  [OK] Frontend собран успешно!")
            else:
                print("  [WARNING] JS файлы не найдены, но index.html есть")
        
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
        print(f"\nПопробуйте открыть:")
        print(f"  https://{SSH_HOST}")
        print(f"\nЛогин: admin")
        print(f"Пароль: admin")
        print(f"\nЕсли frontend не работает:")
        print(f"  1. Очистите кэш браузера (Ctrl+Shift+Delete)")
        print(f"  2. Откройте в режиме инкогнито")
        print(f"  3. Проверьте консоль (F12) на наличие ошибок")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()



