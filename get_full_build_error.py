#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Получение полной информации об ошибке сборки
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
    print("ПОЛНАЯ ИНФОРМАЦИЯ ОБ ОШИБКЕ СБОРКИ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Полный лог ошибки
        print("\n1. ПОЛНЫЙ ЛОГ ОШИБКИ:")
        success, output, error = ssh_exec(ssh, "cat /tmp/vite_build_final2.log")
        print(output)
        
        # 2. Поиск имени файла с ошибкой
        print("\n2. ПОИСК ФАЙЛА С ОШИБКОЙ:")
        if "src/" in output:
            import re
            matches = re.findall(r'src/[^:]+\.tsx?', output)
            if matches:
                print(f"  Файлы с ошибками: {set(matches)}")
        
        # 3. Проверка Sidebar.tsx на сервере
        print("\n3. ПРОВЕРКА SIDEBAR.TSX НА СЕРВЕРЕ:")
        success, output, error = ssh_exec(ssh, f"head -20 {FRONTEND_DIR}/src/components/Sidebar.tsx")
        print(output)
        
        # 4. Проверка синтаксиса TypeScript
        print("\n4. ПРОВЕРКА СИНТАКСИСА:")
        success, output, error = ssh_exec(ssh, f"cd {FRONTEND_DIR} && npx tsc --noEmit --skipLibCheck src/components/Sidebar.tsx 2>&1 | head -20")
        print(output)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()



