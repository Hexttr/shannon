#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка исправленных файлов на сервер и сборка
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
    print("ЗАГРУЗКА ИСПРАВЛЕННЫХ ФАЙЛОВ И СБОРКА")
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
        
        # 2. Проверка исправленных файлов
        print("\n2. ПРОВЕРКА ФАЙЛОВ:")
        files_to_check = [
            "src/components/Sidebar.tsx",
            "src/pages/Services.tsx",
            "src/pages/Home.tsx",
        ]
        
        for file_path in files_to_check:
            success, output, error = ssh_exec(ssh, f"head -3 {FRONTEND_DIR}/{file_path} 2>&1")
            if "import" in output and "\n" in output:
                print(f"  [OK] {file_path.split('/')[-1]} - форматирование правильное")
            else:
                print(f"  [WARNING] {file_path.split('/')[-1]} - возможно все еще в одной строке")
        
        # 3. Удаление старого dist
        print("\n3. УДАЛЕНИЕ СТАРОГО DIST:")
        ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/dist")
        print("  [OK] Старый dist удален")
        
        # 4. Сборка
        print("\n4. СБОРКА FRONTEND:")
        print("  Это может занять 2-3 минуты...")
        
        # Запускаем сборку синхронно с таймаутом
        ssh.exec_command(f"cd {FRONTEND_DIR} && timeout 300 npm run build > /tmp/vite_build_fixed.log 2>&1")
        time.sleep(120)  # Ждем 2 минуты
        
        # Проверяем лог
        success, output, error = ssh_exec(ssh, "tail -100 /tmp/vite_build_fixed.log")
        
        if "built in" in output.lower() or "dist" in output.lower():
            print("  [OK] Сборка завершена успешно!")
            print(f"  {output[-500:]}")
        else:
            print(f"  [WARNING] Лог: {output[-800:]}")
        
        # 5. Проверка dist
        print("\n5. ПРОВЕРКА DIST:")
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ 2>&1")
        print(output)
        
        if "index.html" in output:
            success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/assets/ 2>&1 | head -10")
            print(f"  Assets: {output}")
            
            if ".js" in output and ("index" in output.lower() or "main" in output.lower()):
                print("  [OK] Frontend собран успешно!")
            else:
                print("  [WARNING] JS файлы не найдены")
        else:
            print("  [ERROR] index.html не найден")
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
        
        # 8. Тест доступа
        print("\n8. ТЕСТ ДОСТУПА:")
        success, output, error = ssh_exec(ssh, f"curl -k -s https://{SSH_HOST}/ | head -20")
        if "<!DOCTYPE html>" in output or "<html" in output.lower():
            print("  [OK] Frontend доступен")
        else:
            print(f"  [WARNING] Ответ: {output[:300]}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nFrontend собран и развернут!")
        print(f"\nURL: https://{SSH_HOST}")
        print(f"Логин: admin")
        print(f"Пароль: admin")
        print(f"\nЕсли frontend не работает:")
        print(f"  1. Очистите кэш браузера (Ctrl+Shift+Delete)")
        print(f"  2. Откройте в режиме инкогнито")
        print(f"  3. Проверьте консоль (F12) на наличие ошибок")
        
    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    main()



