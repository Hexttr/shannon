#!/usr/bin/env python3
"""
Скрипт для перезапуска backend
"""

import paramiko
import sys
import time

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def execute_ssh_command(ssh, command, description):
    """Выполняет команду через SSH и выводит результат"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Выполняю: {command}")
    
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    
    output = stdout.read().decode('utf-8', errors='replace')
    errors = stderr.read().decode('utf-8', errors='replace')
    
    if output:
        try:
            print(output)
        except UnicodeEncodeError:
            print(output.encode('ascii', 'replace').decode('ascii'))
    if errors:
        try:
            print(f"Ошибки: {errors}", file=sys.stderr)
        except UnicodeEncodeError:
            print(f"Ошибки: {errors.encode('ascii', 'replace').decode('ascii')}", file=sys.stderr)
    
    return exit_status == 0, output

def main():
    print("="*60)
    print("ПЕРЕЗАПУСК BACKEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        print("Подключение установлено!")
    except Exception as e:
        print(f"Ошибка подключения: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 1. Останавливаем старый процесс
        print("\n1. Останавливаю старый процесс backend...")
        execute_ssh_command(
            ssh,
            "pkill -f 'python.*uvicorn.*app.main:socketio_app' || pkill -f 'python.*run.py' || true",
            "Остановка backend"
        )
        
        time.sleep(2)
        
        # 2. Проверяем наличие venv
        print("\n2. Проверяю наличие venv...")
        execute_ssh_command(
            ssh,
            "test -d /root/shannon/backend/venv && echo 'venv exists' || echo 'venv not found'",
            "Проверка venv"
        )
        
        # 3. Запускаем backend
        print("\n3. Запускаю backend...")
        execute_ssh_command(
            ssh,
            "cd /root/shannon/backend && python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 > /tmp/shannon-backend.log 2>&1 &",
            "Запуск backend"
        )
        
        time.sleep(3)
        
        # 4. Проверяем запуск
        print("\n4. Проверяю запуск backend...")
        execute_ssh_command(
            ssh,
            "ps aux | grep -E 'python.*uvicorn|python.*run.py' | grep -v grep",
            "Процессы backend"
        )
        
        execute_ssh_command(
            ssh,
            "ss -tlnp | grep :8000 || netstat -tlnp | grep :8000",
            "Порт 8000"
        )
        
        # 5. Проверяем доступность
        print("\n5. Проверяю доступность backend...")
        execute_ssh_command(
            ssh,
            "curl -s http://127.0.0.1:8000/health",
            "Проверка /health"
        )
        
        execute_ssh_command(
            ssh,
            "curl -s http://127.0.0.1:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"513277\"}' | head -3",
            "Проверка API"
        )
        
        # 6. Проверяем логи на ошибки
        print("\n6. Проверяю логи backend...")
        execute_ssh_command(
            ssh,
            "tail -20 /tmp/shannon-backend.log",
            "Логи backend"
        )
        
        print("\n" + "="*60)
        print("ПЕРЕЗАПУСК ЗАВЕРШЕН")
        print("="*60)
        print(f"\nBackend API: http://{SSH_HOST}/api/")
        print(f"Frontend: http://{SSH_HOST}/")
        
    except Exception as e:
        print(f"\nКритическая ошибка: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        ssh.close()
        print("\nСоединение закрыто.")

if __name__ == "__main__":
    main()

