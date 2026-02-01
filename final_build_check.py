#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная проверка и сборка
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
    print("ФИНАЛЬНАЯ ПРОВЕРКА И СБОРКА")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка лога сборки
        print("\n1. ПРОВЕРКА ЛОГА СБОРКИ:")
        success, output, error = ssh_exec(ssh, "cat /tmp/vite_build_fixed.log | tail -50")
        print(output[-1000:])
        
        # 2. Удаление старого dist
        print("\n2. УДАЛЕНИЕ СТАРОГО DIST:")
        ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/dist")
        print("  [OK] Старый dist удален")
        
        # 3. Сборка с ожиданием завершения
        print("\n3. СБОРКА FRONTEND:")
        print("  Запускаем сборку и ждем завершения...")
        
        # Запускаем сборку и ждем
        stdin, stdout, stderr = ssh.exec_command(f"cd {FRONTEND_DIR} && npm run build 2>&1")
        
        # Ждем завершения (максимум 5 минут)
        start_time = time.time()
        timeout = 300
        
        output_lines = []
        while True:
            if stdout.channel.exit_status_ready():
                break
            if time.time() - start_time > timeout:
                print("  [WARNING] Таймаут ожидания")
                break
            time.sleep(2)
        
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8', errors='replace')
        error = stderr.read().decode('utf-8', errors='replace')
        
        print(f"  Статус выхода: {exit_status}")
        print(f"  Вывод: {output[-800:]}")
        if error:
            print(f"  Ошибки: {error[-500:]}")
        
        # 4. Проверка dist
        print("\n4. ПРОВЕРКА DIST:")
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ 2>&1")
        if "No such file" in output:
            print("  [ERROR] dist не создан")
            print("  Попробуем собрать еще раз...")
            
            # Повторная попытка
            stdin, stdout, stderr = ssh.exec_command(f"cd {FRONTEND_DIR} && timeout 300 npm run build 2>&1")
            time.sleep(180)  # Ждем 3 минуты
            
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8', errors='replace')
            
            print(f"  Повторная сборка - статус: {exit_status}")
            print(f"  Вывод: {output[-500:]}")
            
            # Проверяем снова
            success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ 2>&1")
            print(f"  Проверка dist: {output}")
        else:
            print(f"  [OK] dist создан!")
            print(output)
            
            # Проверяем assets
            success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/assets/ 2>&1 | head -10")
            print(f"  Assets: {output}")
        
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
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()


