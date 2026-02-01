#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка и исправление отсутствующих компонентов
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def check_and_fix():
    """Проверяет и исправляет отсутствующие компоненты"""
    print("Проверка компонентов...")
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # Проверяем наличие компонентов
        print("\n[1] Проверка компонентов:")
        output, error, code = conn.execute("ls -la /root/shannon/template/src/components/ | grep -E 'LogViewer|StatusBar|VulnerabilitiesList'")
        print(output)
        
        # Если LogViewer отсутствует, создаем его из локального файла
        output, error, code = conn.execute("test -f /root/shannon/template/src/components/LogViewer.tsx && echo 'EXISTS' || echo 'NOT_FOUND'")
        if 'NOT_FOUND' in output:
            print("\n[2] LogViewer.tsx не найден, создаем...")
            if os.path.exists("template/src/components/LogViewer.tsx"):
                with open("template/src/components/LogViewer.tsx", 'r', encoding='utf-8') as f:
                    logviewer_content = f.read()
                
                import paramiko
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect("72.56.79.153", port=22, username="root", password="m8J@2_6whwza6U", timeout=10)
                sftp = ssh.open_sftp()
                with sftp.file("/root/shannon/template/src/components/LogViewer.tsx", 'w') as remote_file:
                    remote_file.write(logviewer_content)
                sftp.close()
                ssh.close()
                print("[OK] LogViewer.tsx создан")
            else:
                print("[ERROR] Локальный LogViewer.tsx не найден")
        
        # Проверяем другие компоненты
        for component in ['StatusBar.tsx', 'VulnerabilitiesList.tsx']:
            output, error, code = conn.execute(f"test -f /root/shannon/template/src/components/{component} && echo 'EXISTS' || echo 'NOT_FOUND'")
            if 'NOT_FOUND' in output:
                print(f"\n[{component}] не найден, проверяем локально...")
                if os.path.exists(f"template/src/components/{component}"):
                    with open(f"template/src/components/{component}", 'r', encoding='utf-8') as f:
                        comp_content = f.read()
                    
                    import paramiko
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect("72.56.79.153", port=22, username="root", password="m8J@2_6whwza6U", timeout=10)
                    sftp = ssh.open_sftp()
                    with sftp.file(f"/root/shannon/template/src/components/{component}", 'w') as remote_file:
                        remote_file.write(comp_content)
                    sftp.close()
                    ssh.close()
                    print(f"[OK] {component} создан")
        
        # Пересборка
        print("\n[3] Пересборка фронтенда...")
        output, error, code = conn.execute("cd /root/shannon/template && npm run build 2>&1")
        
        if output:
            lines = output.split('\n')
            if 'ERROR' in output or 'error' in output.lower() or code != 0:
                print('\n'.join(lines[-40:]))
            else:
                print('\n'.join(lines[-15:]))
        
        if code == 0:
            print("\n[OK] Фронтенд успешно собран!")
            output, error, code = conn.execute("test -f /root/shannon/template/dist/index.html && ls -lh /root/shannon/template/dist/index.html || echo 'NOT FOUND'")
            print(f"\n[4] Результат:\n{output}")
            return True
        else:
            print("\n[ERROR] Ошибка сборки!")
            return False

if __name__ == "__main__":
    success = check_and_fix()
    sys.exit(0 if success else 1)

