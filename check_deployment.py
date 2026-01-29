#!/usr/bin/env python3
"""
Скрипт для проверки развертывания
"""

import paramiko
import sys

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
FRONTEND_DIR = "/root/shannon/template"

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
    print("ПРОВЕРКА РАЗВЕРТЫВАНИЯ")
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
        # 1. Проверяем наличие dist
        print("\n1. Проверяю наличие dist...")
        success, output = execute_ssh_command(
            ssh,
            f"ls -la {FRONTEND_DIR}/dist/ 2>&1 | head -20",
            "Содержимое dist"
        )
        
        # 2. Проверяем наличие index.html
        print("\n2. Проверяю наличие index.html...")
        execute_ssh_command(
            ssh,
            f"test -f {FRONTEND_DIR}/dist/index.html && echo 'index.html exists' || echo 'index.html not found'",
            "Проверка index.html"
        )
        
        # 3. Проверяем логи nginx
        print("\n3. Проверяю логи nginx...")
        execute_ssh_command(
            ssh,
            "tail -30 /var/log/nginx/error.log",
            "Последние ошибки nginx"
        )
        
        # 4. Проверяем доступность backend
        print("\n4. Проверяю доступность backend...")
        execute_ssh_command(
            ssh,
            "curl -s http://localhost:8000/docs | head -5",
            "Проверка backend на localhost:8000"
        )
        
        # 5. Проверяем конфигурацию nginx
        print("\n5. Проверяю конфигурацию nginx...")
        execute_ssh_command(
            ssh,
            "cat /etc/nginx/sites-available/shannon",
            "Конфигурация nginx"
        )
        
        # 6. Проверяем права доступа
        print("\n6. Проверяю права доступа...")
        execute_ssh_command(
            ssh,
            f"ls -la {FRONTEND_DIR}/dist/ | head -5",
            "Права доступа к dist"
        )
        
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

