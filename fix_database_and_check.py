#!/usr/bin/env python3
"""
Исправление базы данных и проверка причины зависания
"""

import paramiko

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ИСПРАВЛЕНИЕ БАЗЫ ДАННЫХ И ПРОВЕРКА")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Исправляем базу данных - добавляем недостающие колонки
        print("\n1. ИСПРАВЛЕНИЕ БАЗЫ ДАННЫХ:")
        stdin, stdout, stderr = ssh.exec_command("""
cd /root/shannon/backend && python3 << 'PYEOF'
import sqlite3

conn = sqlite3.connect('shannon.db')
cursor = conn.cursor()

# Проверяем существующие колонки
cursor.execute("PRAGMA table_info(pentests)")
columns = [col[1] for col in cursor.fetchall()]
print(f"Существующие колонки: {columns}")

# Добавляем current_step если нет
if 'current_step' not in columns:
    try:
        cursor.execute("ALTER TABLE pentests ADD COLUMN current_step VARCHAR")
        print("[OK] Добавлена колонка current_step")
    except Exception as e:
        print(f"[ERROR] Не удалось добавить current_step: {e}")

# Добавляем step_progress если нет
if 'step_progress' not in columns:
    try:
        cursor.execute("ALTER TABLE pentests ADD COLUMN step_progress TEXT")
        print("[OK] Добавлена колонка step_progress")
    except Exception as e:
        print(f"[ERROR] Не удалось добавить step_progress: {e}")

conn.commit()
conn.close()
print("[OK] База данных исправлена")
PYEOF
""")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)
        error_output = stderr.read().decode('utf-8', errors='replace')
        if error_output:
            print(f"ERROR: {error_output}")
        
        # 2. Проверяем логи пентеста
        print("\n2. ЛОГИ ПЕНТЕСТА:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT timestamp, level, substr(message, 1, 100) FROM logs WHERE pentest_id = 1 ORDER BY timestamp;'")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            lines = output.split('\n')
            for line in lines[:20]:
                print(line)
        else:
            print("Логи не найдены")
        
        # 3. Проверяем ошибки в логах backend
        print("\n3. ОШИБКИ В ЛОГАХ BACKEND:")
        stdin, stdout, stderr = ssh.exec_command("grep -i -E 'error|exception|traceback|failed|fail' /tmp/shannon-backend.log | tail -30")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            print(output[:2000])
        else:
            print("Ошибок не найдено")
        
        # 4. Проверяем что произошло с пентестом
        print("\n4. СТАТУС ПЕНТЕСТА:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, name, status, started_at, completed_at FROM pentests WHERE id = 1;'")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)
        
        # 5. Перезапускаем backend
        print("\n5. ПЕРЕЗАПУСК BACKEND:")
        stdin, stdout, stderr = ssh.exec_command("pkill -f 'python.*uvicorn.*app.main:socketio_app' || true")
        stdout.channel.recv_exit_status()
        
        import time
        time.sleep(2)
        
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 > /tmp/shannon-backend.log 2>&1 &")
        stdout.channel.recv_exit_status()
        
        time.sleep(3)
        
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'uvicorn|python.*app.main' | grep -v grep")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            print("[OK] Backend перезапущен")
        else:
            print("[ERROR] Backend не запустился")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

