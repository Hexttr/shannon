#!/usr/bin/env python3
"""
Деплой улучшений: проверка self-scanning и workflow tracking
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
    print("ДЕПЛОЙ УЛУЧШЕНИЙ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    sftp = ssh.open_sftp()
    
    try:
        # Загружаем исправленные файлы
        print("\n1. Загружаю исправленные файлы...")
        files_to_upload = [
            ('backend/app/models/pentest.py', '/root/shannon/backend/app/models/pentest.py'),
            ('backend/app/core/pentest_engine.py', '/root/shannon/backend/app/core/pentest_engine.py'),
            ('backend/app/schemas/pentest.py', '/root/shannon/backend/app/schemas/pentest.py'),
        ]
        
        for local, remote in files_to_upload:
            if os.path.exists(local):
                upload_file(sftp, local, remote)
            else:
                print(f"ПРЕДУПРЕЖДЕНИЕ: Файл {local} не найден")
        
        sftp.close()
        
        # Создаем миграцию для новых полей
        print("\n2. Создаю миграцию для новых полей...")
        stdin, stdout, stderr = ssh.exec_command("""
cd /root/shannon/backend && python3 << 'PYEOF'
from app.database import engine, Base
from app.models.pentest import Pentest
from sqlalchemy import inspect

# Проверяем существующие колонки
inspector = inspect(engine)
columns = [col['name'] for col in inspector.get_columns('pentests')]

print("Существующие колонки:", columns)

# Если колонок нет, создаем их через ALTER TABLE
if 'current_step' not in columns:
    print("Добавляю current_step...")
    with engine.connect() as conn:
        conn.execute("ALTER TABLE pentests ADD COLUMN current_step VARCHAR")
        conn.commit()
    print("current_step добавлена")

if 'step_progress' not in columns:
    print("Добавляю step_progress...")
    with engine.connect() as conn:
        conn.execute("ALTER TABLE pentests ADD COLUMN step_progress JSON")
        conn.commit()
    print("step_progress добавлена")

print("Миграция завершена")
PYEOF
""")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)
        
        # Перезапускаем backend
        print("\n3. Перезапускаю backend...")
        stdin, stdout, stderr = ssh.exec_command("pkill -f 'python.*uvicorn.*app.main:socketio_app' || true")
        stdout.channel.recv_exit_status()
        
        import time
        time.sleep(2)
        
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 > /tmp/shannon-backend.log 2>&1 &")
        stdout.channel.recv_exit_status()
        
        time.sleep(3)
        
        # Проверяем что backend запустился
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'uvicorn|python.*app.main' | grep -v grep")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            print("[OK] Backend перезапущен")
        else:
            print("[ERROR] Backend не запустился")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print("\nДобавлено:")
        print("1. Проверка на self-scanning (white box)")
        print("2. Система отслеживания workflow (current_step, step_progress)")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

