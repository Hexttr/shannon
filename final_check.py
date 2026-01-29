#!/usr/bin/env python3
"""
Финальная проверка после исправлений
"""

import paramiko

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ФИНАЛЬНАЯ ПРОВЕРКА")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Проверяем что база исправлена
        print("\n1. ПРОВЕРКА БАЗЫ ДАННЫХ:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'PRAGMA table_info(pentests);'")
        output = stdout.read().decode('utf-8', errors='replace')
        columns = [line.split('|')[1] for line in output.split('\n') if '|' in line]
        if 'current_step' in columns and 'step_progress' in columns:
            print("[OK] Колонки current_step и step_progress существуют")
        else:
            print("[ERROR] Колонки не найдены")
        
        # Проверяем статус пентеста
        print("\n2. СТАТУС ПЕНТЕСТА:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, name, status, current_step FROM pentests WHERE id = 1;'")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output if output else "Пентест не найден")
        
        # Проверяем что backend работает
        print("\n3. BACKEND:")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/api/pentests -H 'Authorization: Bearer test' 2>&1 | head -5")
        output = stdout.read().decode('utf-8', errors='replace')
        if 'OperationalError' not in output:
            print("[OK] Backend отвечает (ошибка авторизации ожидаема)")
        else:
            print("[ERROR] Backend имеет проблемы с базой данных")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
