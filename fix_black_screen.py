#!/usr/bin/env python3
"""
Исправление черного экрана - пересборка frontend с исправлениями
"""

import paramiko
import sys
import time

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def execute_ssh_command(ssh, command, description):
    print(f"\n{description}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error_output = stderr.read().decode('utf-8', errors='replace')
    if output:
        try:
            print(output[:1000])
        except:
            print(output[:1000].encode('ascii', 'replace').decode('ascii'))
    if error_output:
        try:
            print("ERROR:", error_output[:500])
        except:
            print("ERROR:", error_output[:500].encode('ascii', 'replace').decode('ascii'))
    return exit_status == 0, output

def main():
    print("="*60)
    print("ИСПРАВЛЕНИЕ ЧЕРНОГО ЭКРАНА")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Копируем исправленные файлы
        print("\n1. Копирую исправленные файлы...")
        
        # App.tsx
        with open('template/src/App.tsx', 'r', encoding='utf-8') as f:
            app_content = f.read()
        stdin, stdout, stderr = ssh.exec_command(f"cat > /root/shannon/template/src/App.tsx << 'EOF'\n{app_content}\nEOF\n")
        stdout.channel.recv_exit_status()
        
        # AuthContext.tsx
        with open('template/src/contexts/AuthContext.tsx', 'r', encoding='utf-8') as f:
            auth_content = f.read()
        stdin, stdout, stderr = ssh.exec_command(f"cat > /root/shannon/template/src/contexts/AuthContext.tsx << 'EOF'\n{auth_content}\nEOF\n")
        stdout.channel.recv_exit_status()
        
        # Login.tsx
        with open('template/src/pages/Login.tsx', 'r', encoding='utf-8') as f:
            login_content = f.read()
        stdin, stdout, stderr = ssh.exec_command(f"cat > /root/shannon/template/src/pages/Login.tsx << 'EOF'\n{login_content}\nEOF\n")
        stdout.channel.recv_exit_status()
        
        print("Файлы скопированы")
        
        # 2. Пересобираем frontend
        print("\n2. Пересобираю frontend...")
        execute_ssh_command(
            ssh,
            "cd /root/shannon/template && npm run build 2>&1",
            "Сборка frontend"
        )
        
        # 3. Копируем dist
        print("\n3. Копирую dist...")
        execute_ssh_command(
            ssh,
            "rm -rf /var/www/shannon/* && cp -r /root/shannon/template/dist/* /var/www/shannon/ && chown -R www-data:www-data /var/www/shannon && chmod -R 755 /var/www/shannon",
            "Копирование dist"
        )
        
        # 4. Проверяем что файлы на месте
        print("\n4. Проверяю файлы...")
        execute_ssh_command(
            ssh,
            "ls -la /var/www/shannon/ | head -10",
            "Список файлов"
        )
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nОткройте: https://{SSH_HOST}/")
        print("Проверьте консоль браузера для debug логов")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

