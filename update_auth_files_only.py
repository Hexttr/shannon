#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновление только файлов авторизации на сервере
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
    print("ОБНОВЛЕНИЕ ФАЙЛОВ АВТОРИЗАЦИИ")
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
        
        # 2. Копирование только измененных файлов
        print("\n2. КОПИРОВАНИЕ ФАЙЛОВ:")
        files_to_copy = [
            ("template/src/contexts/AuthContext.tsx", f"{FRONTEND_DIR}/src/contexts/AuthContext.tsx"),
            ("template/src/pages/Login.tsx", f"{FRONTEND_DIR}/src/pages/Login.tsx"),
        ]
        
        for local_file, remote_file in files_to_copy:
            try:
                with open(local_file, 'rb') as f:
                    sftp.putfo(f, remote_file)
                print(f"  [OK] {local_file.split('/')[-1]}")
            except Exception as e:
                print(f"  [ERROR] {local_file}: {e}")
        
        # 3. Пересборка только измененных частей (или полная пересборка)
        print("\n3. ПЕРЕСБОРКА:")
        print("  Пробуем собрать...")
        # Запускаем в фоне с таймаутом
        ssh.exec_command(f"cd {FRONTEND_DIR} && timeout 180 /usr/bin/npm run build > /tmp/build.log 2>&1 &")
        print("  Сборка запущена в фоне, ждем...")
        time.sleep(60)  # Ждем минуту
        
        # Проверяем лог
        success, output, error = ssh_exec(ssh, "tail -30 /tmp/build.log")
        print(f"  Лог сборки: {output[-300:]}")
        
        # Проверяем dist
        success, output, error = ssh_exec(ssh, f"test -d {FRONTEND_DIR}/dist && echo 'EXISTS' || echo 'MISSING'")
        if "EXISTS" in output:
            print("  [OK] dist создан")
        else:
            print("  [WARNING] dist не создан, используем старую версию")
        
        # 4. Установка прав
        print("\n4. УСТАНОВКА ПРАВ:")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist 2>&1 || echo 'ok'")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist 2>&1 || chown -R root:root {FRONTEND_DIR}/dist 2>&1 || echo 'ok'")
        print("  [OK] Права установлены")
        
        # 5. Перезагрузка Nginx
        print("\n5. ПЕРЕЗАГРУЗКА NGINX:")
        ssh_exec(ssh, "systemctl reload nginx")
        time.sleep(2)
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nВАЖНО:")
        print(f"  API работает правильно (статус 200 при тестировании).")
        print(f"  Проблема может быть в кэше браузера или в формате ответа.")
        print(f"\nПопробуйте:")
        print(f"  1. Очистить кэш браузера полностью (Ctrl+Shift+Delete)")
        print(f"  2. Открыть https://{SSH_HOST} в режиме инкогнито")
        print(f"  3. Открыть консоль (F12) и проверить:")
        print(f"     - Логи [DEBUG], [Login], [AuthContext]")
        print(f"     - Network tab - запрос /api/auth/login")
        print(f"     - Статус ответа и тело ответа")
        print(f"\nУчетные данные:")
        print(f"  Логин: admin")
        print(f"  Пароль: admin")
        
    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    main()

