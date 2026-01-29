#!/usr/bin/env python3
"""
Проверка нагрузки на сервер и статуса пентеста
"""

import paramiko

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("ПРОВЕРКА НАГРУЗКИ НА СЕРВЕР И СТАТУСА ПЕНТЕСТА")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Общая нагрузка на систему
        print("\n1. НАГРУЗКА НА СИСТЕМУ:")
        stdin, stdout, stderr = ssh.exec_command("top -bn1 | head -20")
        output = stdout.read().decode('utf-8', errors='replace')
        try:
            print(output)
        except:
            print(output.encode('ascii', 'replace').decode('ascii'))
        
        # 2. Использование памяти
        print("\n2. ИСПОЛЬЗОВАНИЕ ПАМЯТИ:")
        stdin, stdout, stderr = ssh.exec_command("free -h")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)
        
        # 3. Использование CPU
        print("\n3. ИСПОЛЬЗОВАНИЕ CPU:")
        stdin, stdout, stderr = ssh.exec_command("mpstat 1 3 | tail -5")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output if output else "mpstat не установлен")
        
        # 4. Активные процессы пентестинга
        print("\n4. АКТИВНЫЕ ПРОЦЕССЫ ПЕНТЕСТИНГА:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'nmap|nikto|nuclei|sqlmap|dirb|gobuster|wpscan|whatweb|subfinder|httpx' | grep -v grep")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            print(output)
        else:
            print("Нет активных процессов пентестинга")
        
        # 5. Статус пентеста в базе данных
        print("\n5. СТАТУС ПЕНТЕСТА:")
        stdin, stdout, stderr = ssh.exec_command("""
cd /root/shannon/backend && python3 << 'PYEOF'
from app.database import SessionLocal
from app.models.pentest import Pentest

db = SessionLocal()
pentest = db.query(Pentest).order_by(Pentest.created_at.desc()).first()

if pentest:
    print(f"ID: {pentest.id}")
    print(f"Название: {pentest.name}")
    print(f"URL: {pentest.target_url}")
    print(f"Статус: {pentest.status.value if hasattr(pentest.status, 'value') else pentest.status}")
    print(f"Текущий шаг: {pentest.current_step if hasattr(pentest, 'current_step') else 'N/A'}")
    print(f"Прогресс шагов: {pentest.step_progress if hasattr(pentest, 'step_progress') else 'N/A'}")
    print(f"Запущен: {pentest.started_at}")
    print(f"Завершен: {pentest.completed_at if pentest.completed_at else 'Нет'}")
else:
    print("Пентесты не найдены")
PYEOF
""")
        output = stdout.read().decode('utf-8', errors='replace')
        print(output)
        
        # 6. Последние логи пентеста
        print("\n6. ПОСЛЕДНИЕ ЛОГИ ПЕНТЕСТА (последние 10):")
        stdin, stdout, stderr = ssh.exec_command("""
cd /root/shannon/backend && python3 << 'PYEOF'
from app.database import SessionLocal
from app.models.pentest import Pentest
from app.models.log import Log

db = SessionLocal()
pentest = db.query(Pentest).order_by(Pentest.created_at.desc()).first()

if pentest:
    logs = db.query(Log).filter(Log.pentest_id == pentest.id).order_by(Log.timestamp.desc()).limit(10).all()
    print(f"Всего логов: {db.query(Log).filter(Log.pentest_id == pentest.id).count()}")
    for log in reversed(logs):
        level = log.level.value if hasattr(log.level, 'value') else str(log.level)
        print(f"[{log.timestamp}] [{level}] {log.message}")
else:
    print("Пентесты не найдены")
PYEOF
""")
        output = stdout.read().decode('utf-8', errors='replace')
        try:
            print(output)
        except:
            print(output.encode('ascii', 'replace').decode('ascii'))
        
        # 7. Проверка зависших процессов
        print("\n7. ПРОВЕРКА ЗАВИСШИХ ПРОЦЕССОВ:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | awk '{if ($3 > 50 || $4 > 50) print $0}' | head -10")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            print("Процессы с высокой нагрузкой (>50% CPU или памяти):")
            print(output)
        else:
            print("Нет процессов с высокой нагрузкой")
        
        # 8. Время работы процессов
        print("\n8. ВРЕМЯ РАБОТЫ ПРОЦЕССОВ:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'nmap|nikto|nuclei|python.*uvicorn' | grep -v grep | awk '{print $2, $10, $11}'")
        output = stdout.read().decode('utf-8', errors='replace')
        if output:
            print("PID | CPU TIME | CMD")
            print(output)
        else:
            print("Нет активных процессов")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

