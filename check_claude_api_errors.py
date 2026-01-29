#!/usr/bin/env python3
"""
Проверка ошибок API Claude и статуса пентеста
"""

import paramiko
import json

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ПРОВЕРКА ОШИБОК API CLAUDE И СТАТУСА ПЕНТЕСТА")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверяем текущий пентест
        print("\n1. СТАТУС ПЕНТЕСТА:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, name, target_url, status, current_step FROM pentests WHERE status = \"RUNNING\" ORDER BY created_at DESC LIMIT 1;'")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            parts = output.strip().split('|')
            if len(parts) >= 5:
                pentest_id, name, target_url, status, current_step = parts[0], parts[1], parts[2], parts[3], parts[4]
                print(f"  ID: {pentest_id}")
                print(f"  Имя: {name}")
                print(f"  Статус: {status}")
                print(f"  Текущий шаг: {current_step}")
            else:
                print(f"  {output}")
        else:
            print("  [INFO] Нет активных пентестов")
            # Проверяем последний пентест
            stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, name, status, current_step FROM pentests ORDER BY created_at DESC LIMIT 1;'")
            last_output = stdout.read().decode('utf-8', errors='replace')
            if last_output:
                print(f"  Последний пентест: {last_output}")
        
        # 2. Проверяем логи на ошибки API Claude
        print("\n2. ОШИБКИ API CLAUDE В ЛОГАХ:")
        if output:
            pentest_id = parts[0] if output else "2"
        else:
            pentest_id = "2"
        
        # Ищем ошибки связанные с Claude API
        error_keywords = [
            "claude",
            "anthropic",
            "api",
            "401",
            "403",
            "429",
            "quota",
            "credit",
            "billing",
            "authentication",
            "unauthorized",
            "forbidden",
            "rate limit",
            "insufficient"
        ]
        
        for keyword in error_keywords:
            stdin, stdout, stderr = ssh.exec_command(f"sqlite3 /root/shannon/backend/shannon.db 'SELECT message FROM logs WHERE pentest_id = {pentest_id} AND (message LIKE \"%{keyword}%\" OR message LIKE \"%{keyword.upper()}%\") ORDER BY timestamp DESC LIMIT 5;'")
            errors = stdout.read().decode('utf-8', errors='replace')
            if errors:
                print(f"\n  Найдены ошибки с ключевым словом '{keyword}':")
                for err in errors.strip().split('\n'):
                    if err and len(err) > 5:
                        safe_err = err.encode('ascii', 'replace').decode('ascii')
                        print(f"    {safe_err[:150]}")
        
        # 3. Проверяем последние логи пентеста
        print("\n3. ПОСЛЕДНИЕ 20 ЛОГОВ ПЕНТЕСТА:")
        stdin, stdout, stderr = ssh.exec_command(f"sqlite3 /root/shannon/backend/shannon.db 'SELECT timestamp, level, message FROM logs WHERE pentest_id = {pentest_id} ORDER BY timestamp DESC LIMIT 20;'")
        logs = stdout.read().decode('utf-8', errors='replace')
        if logs:
            for log in logs.strip().split('\n'):
                if log and len(log) > 5:
                    safe_log = log.encode('ascii', 'replace').decode('ascii')
                    print(f"  {safe_log[:200]}")
                    # Проверяем на ошибки
                    if 'ERROR' in log.upper() or 'FAILED' in log.upper() or '401' in log or '403' in log or '429' in log:
                        print(f"    [WARNING] Обнаружена ошибка!")
        else:
            print("  [INFO] Логи не найдены")
        
        # 4. Проверяем логи backend на ошибки API
        print("\n4. ЛОГИ BACKEND (последние 30 строк):")
        stdin, stdout, stderr = ssh.exec_command("tail -30 /root/shannon/backend/app.log 2>/dev/null | grep -iE 'claude|anthropic|api|error|401|403|429' || echo 'Логи не найдены или ошибок нет'")
        backend_logs = stdout.read().decode('utf-8', errors='replace')
        if backend_logs and 'не найдены' not in backend_logs.lower():
            print("  Найдены ошибки в логах backend:")
            for line in backend_logs.strip().split('\n')[:10]:
                if line:
                    safe_line = line.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_line[:150]}")
        else:
            print("  [OK] Ошибок API в логах backend не найдено")
        
        # 5. Проверяем процессы пентеста
        print("\n5. ПРОЦЕССЫ СКАНИРОВАНИЯ:")
        tools = ["nmap", "nikto", "nuclei", "dirb", "sqlmap"]
        active_tools = []
        for tool in tools:
            stdin, stdout, stderr = ssh.exec_command(f"ps aux | grep {tool} | grep -v grep | wc -l")
            count = int(stdout.read().decode('utf-8', errors='replace').strip() or 0)
            if count > 0:
                active_tools.append(tool)
                print(f"  [ACTIVE] {tool}: {count} процесс(ов)")
        
        if not active_tools:
            print("  [INFO] Нет активных процессов сканирования")
        
        # 6. Проверяем конфигурацию API ключа
        print("\n6. КОНФИГУРАЦИЯ API CLAUDE:")
        stdin, stdout, stderr = ssh.exec_command("grep -E 'ANTHROPIC_API_KEY|claude' /root/shannon/backend/.env 2>/dev/null | head -1 | sed 's/=.*/=***/'")
        api_config = stdout.read().decode('utf-8', errors='replace')
        if api_config:
            print(f"  [OK] API ключ настроен: {api_config.strip()}")
        else:
            print("  [WARNING] API ключ не найден в .env")
        
        print("\n" + "="*60)
        print("АНАЛИЗ")
        print("="*60)
        
        # Анализ результатов
        has_api_errors = False
        if output and status == "RUNNING":
            print("\n[INFO] Пентест в статусе RUNNING")
            if not active_tools:
                print("[WARNING] Нет активных процессов сканирования - возможно пентест завис")
            else:
                print(f"[OK] Активные инструменты: {', '.join(active_tools)}")
        elif output and status in ["FAILED", "STOPPED"]:
            print(f"\n[WARNING] Пентест в статусе {status}")
            has_api_errors = True
        
        print("\nРекомендации:")
        print("  1. Проверьте баланс на счету Anthropic Claude")
        print("  2. Проверьте логи на наличие ошибок 401/403/429")
        print("  3. Если пентест завис - перезапустите его")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

