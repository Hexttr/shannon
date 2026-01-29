#!/usr/bin/env python3
"""
Проверка что пентест не сканирует сам себя
"""

import paramiko
import re

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ПРОВЕРКА SELF-SCANNING")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверяем текущий пентест
        print("\n1. ТЕКУЩИЙ ПЕНТЕСТ:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, name, target_url, status, current_step FROM pentests WHERE status = \"RUNNING\" ORDER BY created_at DESC LIMIT 1;'")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            parts = output.strip().split('|')
            if len(parts) >= 5:
                pentest_id, name, target_url, status, current_step = parts[0], parts[1], parts[2], parts[3], parts[4]
                print(f"  ID: {pentest_id}")
                print(f"  Имя: {name}")
                print(f"  Цель: {target_url}")
                print(f"  Статус: {status}")
                print(f"  Текущий шаг: {current_step}")
                
                # Проверяем что цель не наш сервер
                server_ips = ["72.56.79.153", "127.0.0.1", "localhost"]
                is_self_scan = False
                for ip in server_ips:
                    if ip in target_url:
                        is_self_scan = True
                        break
                
                if is_self_scan:
                    print(f"  [WARNING] Цель содержит IP сервера!")
                else:
                    print(f"  [OK] Цель не совпадает с сервером")
            else:
                print(output)
        else:
            print("  Нет активных пентестов")
            return
        
        # 2. Проверяем запущенные процессы сканирования
        print("\n2. ЗАПУЩЕННЫЕ ПРОЦЕССЫ СКАНИРОВАНИЯ:")
        
        # Dirb
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'dirb|gobuster' | grep -v grep")
        dirb_processes = stdout.read().decode('utf-8', errors='replace')
        if dirb_processes:
            print("  [FOUND] Процессы dirb/gobuster:")
            for line in dirb_processes.strip().split('\n'):
                if line:
                    print(f"    {line}")
                    # Извлекаем URL из команды
                    url_match = re.search(r'https?://[^\s]+|http://[^\s]+', line)
                    if url_match:
                        url = url_match.group(0)
                        print(f"      -> Цель: {url}")
                        if any(ip in url for ip in server_ips):
                            print(f"      [ERROR] СКАНИРУЕТ САМ СЕБЯ!")
                        else:
                            print(f"      [OK] Цель безопасна")
        else:
            print("  [OK] Процессы dirb/gobuster не найдены")
        
        # Другие инструменты
        tools = ["nmap", "nikto", "nuclei", "sqlmap"]
        for tool in tools:
            stdin, stdout, stderr = ssh.exec_command(f"ps aux | grep {tool} | grep -v grep | head -1")
            proc = stdout.read().decode('utf-8', errors='replace')
            if proc:
                print(f"  [FOUND] {tool}: {proc[:100]}")
        
        # 3. Проверяем логи пентеста
        print("\n3. ПОСЛЕДНИЕ ЛОГИ ПЕНТЕСТА:")
        stdin, stdout, stderr = ssh.exec_command(f"sqlite3 /root/shannon/backend/shannon.db 'SELECT message FROM logs WHERE pentest_id = {pentest_id} ORDER BY timestamp DESC LIMIT 20;'")
        logs = stdout.read().decode('utf-8', errors='replace')
        if logs:
            for log in logs.strip().split('\n'):
                if log:
                    print(f"  {log[:150]}")
                    # Проверяем на упоминание нашего сервера
                    if any(ip in log for ip in server_ips):
                        print(f"    [WARNING] Лог содержит IP сервера!")
        
        # 4. Проверяем код проверки self-scanning
        print("\n4. ПРОВЕРКА КОДА SELF-SCANNING:")
        stdin, stdout, stderr = ssh.exec_command("grep -A 10 '_check_self_scanning' /root/shannon/backend/app/core/pentest_engine.py")
        code = stdout.read().decode('utf-8', errors='replace')
        if code:
            print("  [OK] Метод _check_self_scanning найден:")
            print(code[:500])
        else:
            print("  [ERROR] Метод _check_self_scanning не найден!")
        
        # 5. Проверяем сетевую активность
        print("\n5. СЕТЕВАЯ АКТИВНОСТЬ:")
        stdin, stdout, stderr = ssh.exec_command("netstat -tn 2>/dev/null | grep ':80\|:443' | grep ESTABLISHED | head -5")
        connections = stdout.read().decode('utf-8', errors='replace')
        if connections:
            print("  Активные соединения:")
            for conn in connections.strip().split('\n'):
                if conn:
                    print(f"    {conn}")
                    # Проверяем исходящие соединения к нашему IP
                    if '72.56.79.153' in conn and 'ESTABLISHED' in conn:
                        parts = conn.split()
                        if len(parts) >= 5:
                            local_addr = parts[3]
                            remote_addr = parts[4]
                            if '72.56.79.153' in remote_addr:
                                print(f"      [WARNING] Исходящее соединение к серверу!")
        
        print("\n" + "="*60)
        print("ИТОГ")
        print("="*60)
        print("\n[INFO] Проверка завершена")
        print("Если обнаружены предупреждения - пентест может сканировать сам себя")
        print("Если все [OK] - пентест работает безопасно")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

