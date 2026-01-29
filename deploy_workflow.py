#!/usr/bin/env python3
"""
Деплой страницы Workflow
"""

import paramiko
import os

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def upload_file(sftp, local_path, remote_path):
    """Загружает файл через SFTP"""
    print(f"Загружаю {local_path} -> {remote_path}")
    sftp.put(local_path, remote_path)

def main():
    print("="*60)
    print("ДЕПЛОЙ СТРАНИЦЫ WORKFLOW")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    sftp = ssh.open_sftp()
    
    try:
        # Загружаем новые файлы
        print("\n1. Загружаю файлы...")
        files_to_upload = [
            ('template/src/pages/Workflow.tsx', '/root/shannon/template/src/pages/Workflow.tsx'),
            ('template/src/components/Sidebar.tsx', '/root/shannon/template/src/components/Sidebar.tsx'),
            ('template/src/App.tsx', '/root/shannon/template/src/App.tsx'),
            ('template/src/types/index.ts', '/root/shannon/template/src/types/index.ts'),
        ]
        
        for local, remote in files_to_upload:
            if os.path.exists(local):
                upload_file(sftp, local, remote)
            else:
                print(f"ПРЕДУПРЕЖДЕНИЕ: Файл {local} не найден")
        
        sftp.close()
        
        # Пересобираем frontend
        print("\n2. Пересобираю frontend...")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/template && npm run build 2>&1 | tail -15")
        output = stdout.read().decode('utf-8', errors='replace')
        try:
            print(output[:1000])
        except:
            print(output[:1000].encode('ascii', 'replace').decode('ascii'))
        
        # Копируем dist
        print("\n3. Копирую dist...")
        stdin, stdout, stderr = ssh.exec_command("rm -rf /var/www/shannon/* && cp -r /root/shannon/template/dist/* /var/www/shannon/ && chown -R www-data:www-data /var/www/shannon && chmod -R 755 /var/www/shannon")
        stdout.channel.recv_exit_status()
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nСтраница Workflow доступна: https://{SSH_HOST}/home/workflow")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

