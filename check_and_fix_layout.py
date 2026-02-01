#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка и исправление Layout.tsx на сервере
"""

import paramiko
import sys

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
    print("ПРОВЕРКА И ИСПРАВЛЕНИЕ LAYOUT.TSX")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка Layout.tsx на сервере
        print("\n1. ПРОВЕРКА LAYOUT.TSX НА СЕРВЕРЕ:")
        success, output, error = ssh_exec(ssh, f"head -5 {FRONTEND_DIR}/src/components/Layout.tsx")
        print(f"  Первые строки:\n{output}")
        
        # Проверяем, есть ли проблемы
        if "import" in output and "\n" in output:
            print("  [OK] Форматирование выглядит правильным")
        else:
            print("  [WARNING] Возможны проблемы с форматированием")
        
        # 2. Проверка количества строк
        success, output, error = ssh_exec(ssh, f"wc -l {FRONTEND_DIR}/src/components/Layout.tsx")
        print(f"  Количество строк: {output.strip()}")
        
        # 3. Проверка на наличие "Unexpected end of file" проблем
        success, output, error = ssh_exec(ssh, f"tail -5 {FRONTEND_DIR}/src/components/Layout.tsx")
        print(f"  Последние строки:\n{output}")
        
        # 4. Попытка восстановить из stash
        print("\n2. ВОССТАНОВЛЕНИЕ ИЗ STASH:")
        success, output, error = ssh_exec(ssh, "cd /root/shannon && git show stash@{0}:template/src/components/Layout.tsx > /tmp/Layout.tsx 2>&1")
        if success or not error:
            print("  [OK] Файл восстановлен из stash")
            # Проверяем восстановленный файл
            success, output, error = ssh_exec(ssh, "head -5 /tmp/Layout.tsx")
            print(f"  Первые строки восстановленного файла:\n{output}")
            
            # Копируем на место
            ssh_exec(ssh, f"cp /tmp/Layout.tsx {FRONTEND_DIR}/src/components/Layout.tsx")
            print("  [OK] Файл скопирован")
        else:
            print(f"  [WARNING] Не удалось восстановить: {error[:200]}")
        
        # 5. Обновление репозитория
        print("\n3. ОБНОВЛЕНИЕ РЕПОЗИТОРИЯ:")
        ssh_exec(ssh, "cd /root/shannon && git pull")
        print("  [OK] Репозиторий обновлен")
        
        # 6. Финальная проверка
        print("\n4. ФИНАЛЬНАЯ ПРОВЕРКА:")
        success, output, error = ssh_exec(ssh, f"head -10 {FRONTEND_DIR}/src/components/Layout.tsx")
        print(f"  Файл после обновления:\n{output}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()


