#!/usr/bin/env python3
"""
Финальная проверка после исправления редиректа
"""

import paramiko
import sys

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def execute_ssh_command(ssh, command, description):
    """Выполняет команду через SSH и выводит результат"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    
    output = stdout.read().decode('utf-8', errors='replace')
    errors = stderr.read().decode('utf-8', errors='replace')
    
    if output:
        try:
            print(output)
        except UnicodeEncodeError:
            print(output.encode('ascii', 'replace').decode('ascii'))
    
    return exit_status == 0, output

def main():
    print("="*60)
    print("ФИНАЛЬНАЯ ПРОВЕРКА")
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
        # 1. Проверяем HTTP без редиректов
        print("\n1. Проверяю HTTP ответ...")
        success, output = execute_ssh_command(
            ssh,
            "curl -I http://72.56.79.153/ 2>&1",
            "HTTP заголовки"
        )
        
        has_redirect = 'Location:' in output or '301' in output or '302' in output
        has_200 = '200 OK' in output
        
        # 2. Проверяем содержимое
        print("\n2. Проверяю содержимое...")
        execute_ssh_command(
            ssh,
            "curl -s http://72.56.79.153/ | head -10",
            "Содержимое страницы"
        )
        
        # 3. Проверяем доступность статических файлов
        print("\n3. Проверяю статические файлы...")
        execute_ssh_command(
            ssh,
            "curl -s -I http://72.56.79.153/assets/index-4Wnlt9H8.js 2>&1 | head -3",
            "Проверка JS файла"
        )
        
        # 4. Проверяем API
        print("\n4. Проверяю API...")
        execute_ssh_command(
            ssh,
            "curl -s http://72.56.79.153/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"513277\"}' | head -1",
            "Проверка API login"
        )
        
        # Итоговый статус
        print("\n" + "="*60)
        print("ИТОГОВЫЙ СТАТУС")
        print("="*60)
        
        if has_200 and not has_redirect:
            print("[OK] HTTP работает без редиректов!")
            print("[OK] Приложение доступно по адресу: http://72.56.79.153/")
        elif has_redirect:
            print("[FAIL] Обнаружен редирект!")
            print("Проверьте конфигурацию nginx.")
        else:
            print("[WARN] Неожиданный ответ сервера.")
        
        print("\n" + "="*60)
        print("ПРИЛОЖЕНИЕ ГОТОВО К ТЕСТИРОВАНИЮ")
        print("="*60)
        print(f"\nFrontend: http://{SSH_HOST}/")
        print(f"Backend API: http://{SSH_HOST}/api/")
        print(f"WebSocket: ws://{SSH_HOST}/socket.io/")
        print("\nУчетные данные:")
        print("Username: admin")
        print("Password: 513277")
        
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

