#!/usr/bin/env python3
"""
Детальная проверка ошибок Claude API
"""

import paramiko
import re

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ДЕТАЛЬНАЯ ПРОВЕРКА ОШИБОК CLAUDE API")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Статус пентеста
        print("\n1. СТАТУС ПЕНТЕСТА:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, status, current_step, started_at FROM pentests WHERE status = \"RUNNING\" ORDER BY created_at DESC LIMIT 1;'")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            parts = output.strip().split('|')
            pentest_id = parts[0]
            status = parts[1]
            current_step = parts[2] if len(parts) > 2 else "unknown"
            started_at = parts[3] if len(parts) > 3 else ""
            print(f"  ID: {pentest_id}")
            print(f"  Статус: {status}")
            print(f"  Текущий шаг: {current_step}")
            print(f"  Запущен: {started_at}")
        else:
            print("  Нет активных пентестов")
            return
        
        # 2. Проверяем все логи с ERROR уровнем
        print("\n2. ВСЕ ОШИБКИ В ЛОГАХ:")
        stdin, stdout, stderr = ssh.exec_command(f"sqlite3 /root/shannon/backend/shannon.db 'SELECT timestamp, level, message FROM logs WHERE pentest_id = {pentest_id} AND level = \"ERROR\" ORDER BY timestamp DESC LIMIT 10;'")
        errors = stdout.read().decode('utf-8', errors='replace')
        if errors:
            print("  Найдены ошибки:")
            for err in errors.strip().split('\n'):
                if err:
                    safe_err = err.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_err[:200]}")
        else:
            print("  [OK] Ошибок не найдено")
        
        # 3. Проверяем логи на упоминание Claude
        print("\n3. ЛОГИ С УПОМИНАНИЕМ CLAUDE:")
        stdin, stdout, stderr = ssh.exec_command(f"sqlite3 /root/shannon/backend/shannon.db 'SELECT timestamp, level, message FROM logs WHERE pentest_id = {pentest_id} AND (message LIKE \"%claude%\" OR message LIKE \"%Claude%\" OR message LIKE \"%CLAUDE%\" OR message LIKE \"%anthropic%\" OR message LIKE \"%API%\" OR message LIKE \"%анализ%\" OR message LIKE \"%анализе%\") ORDER BY timestamp DESC LIMIT 15;'")
        claude_logs = stdout.read().decode('utf-8', errors='replace')
        if claude_logs:
            print("  Найдены логи:")
            for log in claude_logs.strip().split('\n'):
                if log:
                    safe_log = log.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_log[:200]}")
        else:
            print("  [INFO] Логов с упоминанием Claude не найдено")
        
        # 4. Проверяем последние логи после завершения каждого шага
        print("\n4. ЛОГИ ПОСЛЕ ЗАВЕРШЕНИЯ ШАГОВ:")
        steps = ["nmap", "nikto", "nuclei", "dirb"]
        for step in steps:
            stdin, stdout, stderr = ssh.exec_command(f"sqlite3 /root/shannon/backend/shannon.db 'SELECT timestamp, level, message FROM logs WHERE pentest_id = {pentest_id} AND message LIKE \"%{step}%\" ORDER BY timestamp DESC LIMIT 3;'")
            step_logs = stdout.read().decode('utf-8', errors='replace')
            if step_logs:
                print(f"\n  {step.upper()}:")
                for log in step_logs.strip().split('\n')[:3]:
                    if log:
                        safe_log = log.encode('ascii', 'replace').decode('ascii')
                        print(f"    {safe_log[:150]}")
        
        # 5. Проверяем файлы логов backend
        print("\n5. ЛОГИ BACKEND (последние 50 строк):")
        stdin, stdout, stderr = ssh.exec_command("tail -50 /root/shannon/backend/app.log 2>/dev/null | tail -20")
        backend_logs = stdout.read().decode('utf-8', errors='replace')
        if backend_logs:
            print("  Последние строки:")
            for line in backend_logs.strip().split('\n')[-10:]:
                if line:
                    safe_line = line.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_line[:150]}")
                    # Проверяем на ошибки
                    if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', '401', '403', '429', 'quota', 'credit']):
                        print(f"      [WARNING] Обнаружена ошибка!")
        else:
            print("  [INFO] Файл логов не найден")
        
        # 6. Проверяем процесс dirb
        print("\n6. ПРОЦЕСС DIRB:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep dirb | grep -v grep")
        dirb_proc = stdout.read().decode('utf-8', errors='replace')
        if dirb_proc:
            print(f"  [ACTIVE] {dirb_proc[:150]}")
            # Проверяем сколько времени работает
            import re
            time_match = re.search(r'(\d+):(\d+)', dirb_proc)
            if time_match:
                minutes = int(time_match.group(1))
                seconds = int(time_match.group(2))
                total_seconds = minutes * 60 + seconds
                print(f"  Время работы: {minutes} минут {seconds} секунд")
                if total_seconds > 1800:  # 30 минут
                    print(f"  [WARNING] Dirb работает очень долго (>30 минут)")
        else:
            print("  [INFO] Процесс dirb не найден (возможно завершился)")
        
        # 7. Проверяем результаты dirb
        print("\n7. РЕЗУЛЬТАТЫ DIRB:")
        stdin, stdout, stderr = ssh.exec_command("ls -lh /tmp/dirb_*.txt 2>/dev/null | tail -1")
        dirb_file = stdout.read().decode('utf-8', errors='replace').strip()
        if dirb_file:
            print(f"  Файл: {dirb_file}")
            stdin, stdout, stderr = ssh.exec_command(f"tail -5 /tmp/dirb_{pentest_id}.txt 2>/dev/null")
            dirb_output = stdout.read().decode('utf-8', errors='replace')
            if dirb_output:
                print("  Последние строки:")
                print(f"    {dirb_output[:200]}")
        
        # 8. Проверяем уязвимости
        print("\n8. НАЙДЕННЫЕ УЯЗВИМОСТИ:")
        stdin, stdout, stderr = ssh.exec_command(f"sqlite3 /root/shannon/backend/shannon.db 'SELECT COUNT(*) FROM vulnerabilities WHERE pentest_id = {pentest_id};'")
        vuln_count = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"  Всего найдено: {vuln_count}")
        
        stdin, stdout, stderr = ssh.exec_command(f"sqlite3 /root/shannon/backend/shannon.db 'SELECT type, title FROM vulnerabilities WHERE pentest_id = {pentest_id} ORDER BY created_at DESC LIMIT 5;'")
        vulns = stdout.read().decode('utf-8', errors='replace')
        if vulns:
            print("  Последние:")
            for vuln in vulns.strip().split('\n')[:5]:
                if vuln:
                    safe_vuln = vuln.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_vuln[:100]}")
        
        print("\n" + "="*60)
        print("ВЫВОД")
        print("="*60)
        
        # Анализ
        if current_step == "dirb":
            print("\n[INFO] Пентест на шаге dirb")
            if dirb_proc:
                print("[OK] Dirb все еще работает")
            else:
                print("[WARNING] Dirb завершился, но пентест не перешел к следующему шагу")
                print("Возможные причины:")
                print("  1. Ошибка при анализе результатов через Claude API")
                print("  2. Пентест завис")
                print("  3. Ошибка в коде")
        
        if not errors:
            print("\n[OK] Явных ошибок в логах не найдено")
        else:
            print("\n[WARNING] Найдены ошибки - проверьте логи выше")
        
        print("\nРекомендации:")
        print("  1. Проверьте баланс на Anthropic Claude")
        print("  2. Если dirb завершился, но пентест не продолжается - возможна ошибка API")
        print("  3. Проверьте логи backend для деталей")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

