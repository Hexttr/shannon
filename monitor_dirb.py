#!/usr/bin/env python3
"""
Мониторинг dirb процесса - проверка что не сканирует сам себя
"""

import paramiko
import re
import time

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("МОНИТОРИНГ DIRB - ПРОВЕРКА SELF-SCANNING")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Находим процесс dirb
        print("\n1. ПРОЦЕСС DIRB:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep dirb | grep -v grep")
        dirb_proc = stdout.read().decode('utf-8', errors='replace')
        
        if not dirb_proc:
            print("  [INFO] Процесс dirb не найден (возможно завершен)")
            return
        
        print(f"  {dirb_proc}")
        
        # Извлекаем PID и команду
        pid_match = re.search(r'^\s*(\w+)\s+(\d+)', dirb_proc)
        if pid_match:
            pid = pid_match.group(2)
            print(f"  PID: {pid}")
            
            # Извлекаем URL из команды
            url_match = re.search(r'https?://[^\s]+', dirb_proc)
            if url_match:
                target_url = url_match.group(0)
                print(f"  Цель: {target_url}")
                
                # Проверяем что это не наш сервер
                server_ips = ["72.56.79.153", "127.0.0.1", "localhost"]
                is_self = any(ip in target_url for ip in server_ips)
                
                if is_self:
                    print(f"  [ERROR] СКАНИРУЕТ САМ СЕБЯ!")
                else:
                    print(f"  [OK] Цель безопасна: {target_url}")
        
        # 2. Проверяем сетевые соединения процесса
        print("\n2. СЕТЕВЫЕ СОЕДИНЕНИЯ ПРОЦЕССА:")
        if pid_match:
            stdin, stdout, stderr = ssh.exec_command(f"lsof -p {pid} 2>/dev/null | grep -E 'TCP|ESTABLISHED' | head -10")
            connections = stdout.read().decode('utf-8', errors='replace')
            if connections:
                print("  Активные соединения:")
                for conn in connections.strip().split('\n'):
                    if conn:
                        print(f"    {conn}")
                        # Проверяем соединения к нашему серверу
                        if '72.56.79.153' in conn:
                            print(f"      [WARNING] Соединение к серверу обнаружено!")
                        elif '127.0.0.1' in conn or 'localhost' in conn:
                            print(f"      [WARNING] Локальное соединение обнаружено!")
            else:
                print("  [INFO] Соединения не найдены (или нет прав)")
        
        # 3. Проверяем вывод dirb (если файл существует)
        print("\n3. ПРОВЕРКА ВЫВОДА DIRB:")
        stdin, stdout, stderr = ssh.exec_command("find /tmp -name 'dirb_*.txt' -type f -mmin -10 2>/dev/null | head -1")
        dirb_output_file = stdout.read().decode('utf-8', errors='replace').strip()
        
        if dirb_output_file:
            print(f"  Файл: {dirb_output_file}")
            stdin, stdout, stderr = ssh.exec_command(f"tail -20 {dirb_output_file} 2>/dev/null")
            output = stdout.read().decode('utf-8', errors='replace')
            if output:
                print("  Последние строки:")
                for line in output.strip().split('\n')[:10]:
                    if line:
                        print(f"    {line[:100]}")
                        # Проверяем на упоминание нашего сервера
                        if '72.56.79.153' in line or '127.0.0.1' in line:
                            print(f"      [WARNING] Обнаружено упоминание сервера!")
        else:
            print("  [INFO] Файл вывода не найден")
        
        # 4. Проверяем логи пентеста
        print("\n4. ЛОГИ ПЕНТЕСТА (последние 15):")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT message FROM logs WHERE pentest_id = 2 ORDER BY timestamp DESC LIMIT 15;'")
        logs = stdout.read().decode('utf-8', errors='replace')
        if logs:
            for log in logs.strip().split('\n'):
                if log and len(log) > 5:
                    safe_log = log.encode('ascii', 'replace').decode('ascii')
                    print(f"  {safe_log[:120]}")
                    # Проверяем на упоминание нашего сервера
                    if '72.56.79.153' in log or '127.0.0.1' in log:
                        print(f"    [WARNING] Лог содержит IP сервера!")
        
        # 5. Проверяем что проверка self-scanning была вызвана
        print("\n5. ПРОВЕРКА SELF-SCANNING В ЛОГАХ:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT message FROM logs WHERE pentest_id = 2 AND message LIKE \"%self%\" OR message LIKE \"%Проверка пройдена%\" OR message LIKE \"%white box%\" ORDER BY timestamp DESC LIMIT 5;'")
        self_check_logs = stdout.read().decode('utf-8', errors='replace')
        if self_check_logs:
            print("  Найдены логи проверки:")
            for log in self_check_logs.strip().split('\n'):
                if log and len(log) > 5:
                    safe_log = log.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_log}")
        else:
            print("  [INFO] Логи проверки не найдены (возможно проверка не выполнялась)")
        
        print("\n" + "="*60)
        print("ИТОГ")
        print("="*60)
        print("\n[INFO] Проверка завершена")
        print("Если все [OK] - пентест работает безопасно и не сканирует сам себя")
        print("Если есть [WARNING] - требуется дополнительная проверка")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

