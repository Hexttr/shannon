#!/usr/bin/env python3
"""
Деплой исправления обработки ошибок Claude API
"""

import paramiko
import os

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ДЕПЛОЙ ИСПРАВЛЕНИЯ ОБРАБОТКИ ОШИБОК CLAUDE API")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    sftp = ssh.open_sftp()
    
    try:
        # Загружаем исправленные файлы
        print("\n1. Загружаю исправленные файлы...")
        files_to_upload = [
            ('backend/app/core/claude_client.py', '/root/shannon/backend/app/core/claude_client.py'),
            ('backend/app/core/pentest_engine.py', '/root/shannon/backend/app/core/pentest_engine.py'),
        ]
        
        for local, remote in files_to_upload:
            if os.path.exists(local):
                print(f"  Загружаю {local} -> {remote}")
                sftp.put(local, remote)
            else:
                print(f"  [WARNING] Файл {local} не найден")
        
        sftp.close()
        
        # Перезапускаем backend
        print("\n2. Перезапускаю backend...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart shannon-backend 2>&1 || pkill -f 'uvicorn.*app.main' && cd /root/shannon/backend && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &")
        stdout.channel.recv_exit_status()
        
        # Проверяем что backend запустился
        print("\n3. Проверяю статус backend...")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'uvicorn.*app.main' | grep -v grep")
        backend_status = stdout.read().decode('utf-8', errors='replace')
        if backend_status:
            print("  [OK] Backend запущен")
        else:
            print("  [WARNING] Backend не найден в процессах")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print("\nИсправления:")
        print("  1. Улучшена обработка ошибок Claude API")
        print("  2. Пентест не будет зависать при ошибках API")
        print("  3. Добавлено логирование типов ошибок (401, 403, 429, 402)")
        print("\nТеперь при ошибках API:")
        print("  - Пентест продолжит работу")
        print("  - Ошибки будут залогированы")
        print("  - Результаты сканирования сохранятся без анализа")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    import time
    main()

