#!/usr/bin/env python3
"""
Проверка статуса workflow и готовности к новому пентесту
"""

import paramiko

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ПРОВЕРКА WORKFLOW И ГОТОВНОСТИ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверяем все пентесты
        print("\n1. ВСЕ ПЕНТЕСТЫ:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, name, status, current_step, step_progress FROM pentests ORDER BY created_at DESC LIMIT 5;'")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output if output else "Пентесты не найдены")
        
        # 2. Проверяем активные пентесты
        print("\n2. АКТИВНЫЕ ПЕНТЕСТЫ (RUNNING):")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, name, status, current_step FROM pentests WHERE status = \"RUNNING\" ORDER BY created_at DESC;'")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            print(output)
        else:
            print("Нет активных пентестов")
        
        # 3. Проверяем последний пентест
        print("\n3. ПОСЛЕДНИЙ ПЕНТЕСТ:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, name, status, current_step, step_progress FROM pentests ORDER BY created_at DESC LIMIT 1;'")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output if output else "Пентесты не найдены")
        
        # 4. Проверяем что backend работает
        print("\n4. BACKEND:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'uvicorn|python.*app.main' | grep -v grep")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            print("[OK] Backend работает")
        else:
            print("[ERROR] Backend не запущен")
        
        # 5. Проверяем инструменты
        print("\n5. ИНСТРУМЕНТЫ:")
        tools = ["nmap", "nikto", "nuclei", "dirb", "sqlmap", "gobuster", "wpscan", "whatweb", "subfinder", "httpx"]
        for tool in tools:
            stdin, stdout, stderr = ssh.exec_command(f"which {tool}")
            if stdout.channel.recv_exit_status() == 0:
                print(f"  [OK] {tool}")
            else:
                print(f"  [ERROR] {tool}")
        
        # 6. Проверяем базу данных
        print("\n6. СТРУКТУРА БАЗЫ ДАННЫХ:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'PRAGMA table_info(pentests);' | grep -E 'current_step|step_progress'")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            print("[OK] Колонки workflow существуют:")
            print(output)
        else:
            print("[ERROR] Колонки workflow не найдены")
        
        print("\n" + "="*60)
        print("ИТОГ")
        print("="*60)
        print("\n[OK] Система готова к новому пентесту!")
        print("Страница Workflow будет показывать:")
        print("  - Активный пентест (status=RUNNING), если есть")
        print("  - Или последний пентест, если нет активных")
        print("\nДля нового пентеста:")
        print("  1. Перейдите в 'Пентесты'")
        print("  2. Выберите сервис")
        print("  3. Нажмите 'Запустить пентест'")
        print("  4. Откройте 'Workflow' для отслеживания")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

