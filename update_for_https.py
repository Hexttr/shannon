#!/usr/bin/env python3
"""
Обновление переменных окружения и CORS для HTTPS
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
    print("ОБНОВЛЕНИЕ ДЛЯ HTTPS")
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
        # 1. Обновляем CORS настройки в backend
        print("\n1. Обновляю CORS настройки в backend...")
        backend_env_file = "/root/shannon/backend/.env"
        
        stdin, stdout, stderr = ssh.exec_command(f"cat {backend_env_file} 2>/dev/null || echo ''")
        current_env = stdout.read().decode('utf-8', errors='replace')
        
        # Обновляем CORS_ORIGINS для включения HTTPS
        new_cors_origins = 'CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://72.56.79.153","https://72.56.79.153","http://72.56.79.153:5173","http://72.56.79.153:3000","http://72.56.79.153:8000"]'
        
        lines = current_env.split('\n')
        updated_lines = []
        cors_found = False
        
        for line in lines:
            if line.startswith('CORS_ORIGINS='):
                updated_lines.append(new_cors_origins)
                cors_found = True
            else:
                updated_lines.append(line)
        
        if not cors_found:
            updated_lines.append(new_cors_origins)
        
        updated_env = '\n'.join(updated_lines)
        
        stdin, stdout, stderr = ssh.exec_command(f"cat > {backend_env_file} << 'ENV_EOF'\n{updated_env}\nENV_EOF\n")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("CORS настройки обновлены для HTTPS!")
        
        # 2. Обновляем переменные окружения frontend
        print("\n2. Обновляю переменные окружения frontend...")
        frontend_env = """VITE_API_URL=https://72.56.79.153/api
VITE_WS_URL=https://72.56.79.153
"""
        
        frontend_env_file = "/root/shannon/template/.env"
        stdin, stdout, stderr = ssh.exec_command(f"cat > {frontend_env_file} << 'ENV_EOF'\n{frontend_env}\nENV_EOF\n")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print(".env файл для frontend обновлен на HTTPS!")
        
        # 3. Перезапускаем backend для применения CORS
        print("\n3. Перезапускаю backend...")
        execute_ssh_command(
            ssh,
            "pkill -f 'python.*uvicorn.*app.main:socketio_app' || true",
            "Остановка backend"
        )
        
        import time
        time.sleep(2)
        
        execute_ssh_command(
            ssh,
            "cd /root/shannon/backend && python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 > /tmp/shannon-backend.log 2>&1 &",
            "Запуск backend"
        )
        
        time.sleep(3)
        
        # 4. Проверяем запуск backend
        print("\n4. Проверяю запуск backend...")
        execute_ssh_command(
            ssh,
            "ps aux | grep -E 'python.*uvicorn|python.*run.py' | grep -v grep",
            "Процессы backend"
        )
        
        execute_ssh_command(
            ssh,
            "curl -s http://127.0.0.1:8000/health",
            "Проверка health endpoint"
        )
        
        # 5. Пересобираем frontend с новыми переменными
        print("\n5. Пересобираю frontend с HTTPS переменными...")
        execute_ssh_command(
            ssh,
            "cd /root/shannon/template && npm run build 2>&1 | tail -20",
            "Пересборка frontend"
        )
        
        # 6. Копируем обновленный dist
        print("\n6. Копирую обновленный dist...")
        execute_ssh_command(
            ssh,
            "cp -r /root/shannon/template/dist/* /var/www/shannon/ && chown -R www-data:www-data /var/www/shannon && chmod -R 755 /var/www/shannon",
            "Копирование dist"
        )
        
        # 7. Финальная проверка
        print("\n7. Финальная проверка...")
        execute_ssh_command(
            ssh,
            "curl -k -I https://72.56.79.153/ 2>&1 | head -5",
            "Проверка HTTPS"
        )
        
        execute_ssh_command(
            ssh,
            "curl -I http://72.56.79.153/ 2>&1 | grep -E 'HTTP|Location' | head -3",
            "Проверка редиректа HTTP -> HTTPS"
        )
        
        execute_ssh_command(
            ssh,
            "curl -k -s https://72.56.79.153/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"513277\"}' | head -1",
            "Проверка API через HTTPS"
        )
        
        print("\n" + "="*60)
        print("ОБНОВЛЕНИЕ ЗАВЕРШЕНО")
        print("="*60)
        print(f"\nHTTP: http://{SSH_HOST}/ (автоматический редирект на HTTPS)")
        print(f"HTTPS: https://{SSH_HOST}/")
        print(f"Backend API: https://{SSH_HOST}/api/")
        print(f"WebSocket: wss://{SSH_HOST}/socket.io/")
        print("\nПримечание: Используется самоподписанный SSL сертификат.")
        print("Браузер может показать предупреждение о безопасности.")
        print("Нажмите 'Продолжить' или 'Advanced -> Proceed' для доступа.")
        print("\nПроверьте работу в браузере: https://72.56.79.153/")
        
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

