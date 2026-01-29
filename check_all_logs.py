#!/usr/bin/env python3
"""
Проверка всех логов для выяснения причины зависания пентеста
"""

import paramiko

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ПРОВЕРКА ВСЕХ ЛОГОВ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Логи backend (последние 200 строк)
        print("\n1. ЛОГИ BACKEND (последние 200 строк):")
        stdin, stdout, stderr = ssh.exec_command("tail -200 /tmp/shannon-backend.log 2>&1")
        output = stdout.read().decode('utf-8', errors='replace')
        try:
            # Ищем ошибки и предупреждения
            lines = output.split('\n')
            error_lines = [l for l in lines if 'ERROR' in l or 'Exception' in l or 'Traceback' in l or 'Error' in l or 'error' in l.lower()]
            if error_lines:
                print("НАЙДЕНЫ ОШИБКИ:")
                for line in error_lines[-20:]:
                    print(line)
            print("\nПоследние 50 строк логов:")
            for line in lines[-50:]:
                print(line)
        except:
            print(output[:3000].encode('ascii', 'replace').decode('ascii'))
        
        # 2. Статус пентеста в базе данных
        print("\n2. СТАТУС ПЕНТЕСТА В БАЗЕ:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, name, target_url, status, created_at, started_at, completed_at FROM pentests ORDER BY created_at DESC LIMIT 3;'")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output if output else "Пентесты не найдены")
        
        # 3. Все логи пентеста
        print("\n3. ВСЕ ЛОГИ ПЕНТЕСТА:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT timestamp, level, message FROM logs WHERE pentest_id = 1 ORDER BY timestamp;'")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            lines = output.split('\n')
            for line in lines:
                print(line)
        else:
            print("Логи не найдены")
        
        # 4. Проверяем системные логи
        print("\n4. СИСТЕМНЫЕ ЛОГИ (journalctl, последние ошибки):")
        stdin, stdout, stderr = ssh.exec_command("journalctl -n 50 --no-pager 2>&1 | grep -i -E 'error|exception|fail|python|uvicorn' | tail -20")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output if output else "Нет релевантных системных логов")
        
        # 5. Проверяем процессы Python и их потоки
        print("\n5. ПРОЦЕССЫ PYTHON И ПОТОКИ:")
        stdin, stdout, stderr = ssh.exec_command("ps auxf | grep python | grep -v grep")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output if output else "Нет процессов Python")
        
        # 6. Проверяем содержимое файла nmap
        print("\n6. СОДЕРЖИМОЕ ФАЙЛА NMAP:")
        stdin, stdout, stderr = ssh.exec_command("cat /tmp/nmap_1.txt 2>&1")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output[:2000] if output else "Файл пуст")
        
        # 7. Проверяем есть ли ошибки в коде выполнения
        print("\n7. ПРОВЕРКА КОДА PENTEST ENGINE:")
        stdin, stdout, stderr = ssh.exec_command("grep -n 'except\\|raise\\|Error' /root/shannon/backend/app/core/pentest_engine.py | head -20")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output if output else "Не найдено")
        
        # 8. Проверяем подключение SSH
        print("\n8. ПРОВЕРКА SSH КЛИЕНТА:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && python3 -c 'from app.core.ssh_client import SSHClient; ssh = SSHClient(); print(\"Connected:\", ssh.connect()); ssh.disconnect()' 2>&1")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

