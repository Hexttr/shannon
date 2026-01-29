#!/usr/bin/env python3
"""
Расследование ошибки Claude API и исправление
"""

import paramiko
import json

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("РАССЛЕДОВАНИЕ ОШИБКИ CLAUDE API")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверяем логи на ошибки API
        print("\n1. ОШИБКИ API В ЛОГАХ:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT timestamp, level, message FROM logs WHERE pentest_id = 2 AND (message LIKE \"%claude%\" OR message LIKE \"%Claude%\" OR message LIKE \"%API%\" OR message LIKE \"%401%\" OR message LIKE \"%402%\" OR message LIKE \"%403%\" OR message LIKE \"%429%\" OR message LIKE \"%quota%\" OR message LIKE \"%credit%\" OR message LIKE \"%Ошибка%\" OR message LIKE \"%ошибка%\") ORDER BY timestamp DESC LIMIT 20;'")
        api_errors = stdout.read().decode('utf-8', errors='replace')
        if api_errors:
            print("  Найдены ошибки:")
            for err in api_errors.strip().split('\n')[:20]:
                if err:
                    safe_err = err.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_err[:200]}")
        else:
            print("  [INFO] Явных ошибок API в логах не найдено")
        
        # 2. Проверяем все ERROR логи
        print("\n2. ВСЕ ОШИБКИ:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT timestamp, message FROM logs WHERE pentest_id = 2 AND level = \"ERROR\" ORDER BY timestamp DESC LIMIT 10;'")
        errors = stdout.read().decode('utf-8', errors='replace')
        if errors:
            print("  Найдены ошибки:")
            for err in errors.strip().split('\n')[:10]:
                if err:
                    safe_err = err.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_err[:200]}")
        else:
            print("  [OK] Ошибок не найдено")
        
        # 3. Проверяем логи после запуска dirb
        print("\n3. ЛОГИ ПОСЛЕ ЗАПУСКА DIRB:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT timestamp, level, message FROM logs WHERE pentest_id = 2 AND timestamp > \"2026-01-29 09:37:45\" ORDER BY timestamp DESC LIMIT 15;'")
        dirb_logs = stdout.read().decode('utf-8', errors='replace')
        if dirb_logs:
            print("  Логи после запуска dirb:")
            for log in dirb_logs.strip().split('\n')[:15]:
                if log:
                    safe_log = log.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_log[:200]}")
        else:
            print("  [INFO] Логов после запуска dirb не найдено")
        
        # 4. Проверяем файл dirb
        print("\n4. РЕЗУЛЬТАТЫ DIRB:")
        stdin, stdout, stderr = ssh.exec_command("head -50 /tmp/dirb_2.txt 2>/dev/null")
        dirb_results = stdout.read().decode('utf-8', errors='replace')
        if dirb_results:
            print("  Первые 50 строк:")
            print(dirb_results[:1000])
        else:
            print("  [ERROR] Файл результатов не найден")
        
        # 5. Проверяем код обработки ошибок
        print("\n5. ПРОВЕРКА КОДА ОБРАБОТКИ ОШИБОК:")
        stdin, stdout, stderr = ssh.exec_command("grep -A 5 'except.*APIError' /root/shannon/backend/app/core/claude_client.py")
        error_handling = stdout.read().decode('utf-8', errors='replace')
        if error_handling:
            print("  [OK] Обработка ошибок API найдена:")
            print(error_handling[:500])
        else:
            print("  [WARNING] Обработка ошибок API не найдена")
        
        # 6. Проверяем что происходит при анализе dirb
        print("\n6. ПРОВЕРКА АНАЛИЗА DIRB:")
        stdin, stdout, stderr = ssh.exec_command("grep -A 10 '_run_dirb_scan' /root/shannon/backend/app/core/pentest_engine.py | head -20")
        dirb_code = stdout.read().decode('utf-8', errors='replace')
        if dirb_code:
            print("  Код анализа dirb:")
            print(dirb_code[:500])
        
        # 7. Проверяем статус в БД
        print("\n7. СТАТУС В БАЗЕ ДАННЫХ:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, status, current_step, step_progress FROM pentests WHERE id = 2;'")
        db_status = stdout.read().decode('utf-8', errors='replace')
        print(f"  {db_status}")
        
        print("\n" + "="*60)
        print("АНАЛИЗ")
        print("="*60)
        print("\n[INFO] Проблема: Dirb завершился, но анализ через Claude API не прошел")
        print("[INFO] Причина: Закончились средства на API Claude")
        print("[INFO] Решение: Нужно обновить статус пентеста вручную или исправить код")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

