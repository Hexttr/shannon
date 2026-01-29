#!/usr/bin/env python3
"""
Деплой улучшенной обработки ошибок
"""

import paramiko
import os

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ДЕПЛОЙ УЛУЧШЕННОЙ ОБРАБОТКИ ОШИБОК")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    sftp = ssh.open_sftp()
    
    try:
        # Загружаем исправленный файл
        print("\n1. Загружаю исправленный файл...")
        if os.path.exists('backend/app/core/pentest_engine.py'):
            sftp.put('backend/app/core/pentest_engine.py', '/root/shannon/backend/app/core/pentest_engine.py')
            print("  [OK] Файл загружен")
        else:
            print("  [ERROR] Файл не найден")
            return
        
        sftp.close()
        
        print("\n" + "="*60)
        print("ГОТОВО")
        print("="*60)
        print("\nУлучшения:")
        print("  1. Пентест не прерывается при ошибках отдельных шагов")
        print("  2. Ошибки логируются, но выполнение продолжается")
        print("  3. Пентест завершится даже если некоторые шаги не выполнились")
        print("\nТеперь при ошибках API Claude:")
        print("  - Ошибка будет обработана")
        print("  - Пентест продолжит выполнение")
        print("  - Результаты сканирования сохранятся")
        print("  - Пентест завершится корректно")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

