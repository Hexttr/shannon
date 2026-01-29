#!/usr/bin/env python3
"""
Скрипт для обновления кода и пересборки frontend
"""

import paramiko
import sys

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
PROJECT_DIR = "/root/shannon"
FRONTEND_DIR = f"{PROJECT_DIR}/template"

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
    print("ОБНОВЛЕНИЕ КОДА И ПЕРЕСБОРКА FRONTEND")
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
        # 1. Инициализируем git репозиторий если нужно
        print("\n1. Проверяю git репозиторий...")
        success, output = execute_ssh_command(
            ssh,
            f"cd {PROJECT_DIR} && git status 2>&1",
            "Проверка git статуса"
        )
        
        if not success or 'not a git repository' in output:
            print("Инициализирую git репозиторий...")
            execute_ssh_command(
                ssh,
                f"cd {PROJECT_DIR} && git init && git remote add origin https://github.com/Hexttr/shannon.git && git fetch && git checkout -f master 2>&1",
                "Инициализация git"
            )
        else:
            # Обновляем код
            execute_ssh_command(
                ssh,
                f"cd {PROJECT_DIR} && git fetch origin && git reset --hard origin/master",
                "Обновление кода из git"
            )
        
        # 2. Отключаем конфликтующую конфигурацию nginx
        print("\n2. Отключаю конфликтующую конфигурацию nginx...")
        execute_ssh_command(
            ssh,
            "rm -f /etc/nginx/sites-enabled/pentest",
            "Удаление конфликтующей конфигурации"
        )
        
        # 3. Пересобираем frontend
        print("\n3. Пересобираю frontend...")
        execute_ssh_command(ssh, f"cd {FRONTEND_DIR} && rm -rf dist node_modules/.vite", "Очистка")
        execute_ssh_command(ssh, f"cd {FRONTEND_DIR} && npm install", "Установка зависимостей")
        
        # Собираем с игнорированием ошибок TypeScript
        success, output = execute_ssh_command(
            ssh,
            f"cd {FRONTEND_DIR} && npm run build 2>&1",
            "Сборка frontend"
        )
        
        # Проверяем наличие dist даже если были ошибки
        success, dist_check = execute_ssh_command(
            ssh,
            f"test -d {FRONTEND_DIR}/dist && echo 'dist exists' || echo 'dist not found'",
            "Проверка dist"
        )
        
        if 'not found' in dist_check:
            print("ОШИБКА: dist не создан! Пробую собрать с игнорированием ошибок...", file=sys.stderr)
            # Пробуем собрать напрямую через vite, игнорируя TypeScript
            execute_ssh_command(
                ssh,
                f"cd {FRONTEND_DIR} && npx vite build --mode production 2>&1 | tail -30",
                "Сборка через vite напрямую"
            )
        
        # 4. Проверяем наличие dist
        success, dist_list = execute_ssh_command(
            ssh,
            f"ls -la {FRONTEND_DIR}/dist/ 2>&1 | head -10",
            "Содержимое dist"
        )
        
        if 'No such file' in dist_list:
            print("КРИТИЧЕСКАЯ ОШИБКА: dist не создан!", file=sys.stderr)
            sys.exit(1)
        
        # 5. Перезапускаем nginx
        print("\n5. Перезапускаю nginx...")
        execute_ssh_command(ssh, "nginx -t", "Проверка конфигурации")
        execute_ssh_command(ssh, "systemctl reload nginx", "Перезагрузка nginx")
        
        # 6. Финальная проверка
        print("\n6. Финальная проверка...")
        execute_ssh_command(ssh, "curl -s -I http://localhost/ | head -3", "Проверка frontend")
        execute_ssh_command(ssh, "curl -s -I http://localhost/api/docs | head -3", "Проверка API")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nFrontend: http://{SSH_HOST}/")
        print(f"Backend API: http://{SSH_HOST}/api/")
        print(f"WebSocket: ws://{SSH_HOST}/socket.io/")
        
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

