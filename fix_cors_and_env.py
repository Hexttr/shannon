#!/usr/bin/env python3
"""
Скрипт для исправления CORS и переменных окружения
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
    print("ИСПРАВЛЕНИЕ CORS И ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
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
        # 1. Обновляем CORS настройки в backend/.env
        print("\n1. Обновляю CORS настройки в backend...")
        backend_env_file = "/root/shannon/backend/.env"
        
        # Читаем текущий .env
        stdin, stdout, stderr = ssh.exec_command(f"cat {backend_env_file} 2>/dev/null || echo ''")
        current_env = stdout.read().decode('utf-8', errors='replace')
        
        # Обновляем CORS_ORIGINS
        new_cors_origins = 'CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://72.56.79.153","http://72.56.79.153:5173","http://72.56.79.153:3000","http://72.56.79.153:8000"]'
        
        # Заменяем или добавляем CORS_ORIGINS
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
        
        # Сохраняем обновленный .env
        stdin, stdout, stderr = ssh.exec_command(f"cat > {backend_env_file} << 'ENV_EOF'\n{updated_env}\nENV_EOF\n")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("CORS настройки обновлены!")
        else:
            print("Ошибка при обновлении CORS настроек", file=sys.stderr)
        
        # 2. Создаем .env файл для frontend
        print("\n2. Создаю .env файл для frontend...")
        frontend_env = """VITE_API_URL=http://72.56.79.153/api
VITE_WS_URL=http://72.56.79.153
"""
        
        frontend_env_file = "/root/shannon/template/.env"
        stdin, stdout, stderr = ssh.exec_command(f"cat > {frontend_env_file} << 'ENV_EOF'\n{frontend_env}\nENV_EOF\n")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print(".env файл для frontend создан!")
        else:
            print("Ошибка при создании .env файла", file=sys.stderr)
        
        # 3. Перезапускаем backend для применения новых CORS настроек
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
            "cd /root/shannon/backend && source venv/bin/activate && nohup python run.py > /tmp/shannon-backend.log 2>&1 &",
            "Запуск backend"
        )
        
        time.sleep(3)
        
        # 4. Проверяем, что backend запустился
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
        
        # 5. Проверяем CORS заголовки
        print("\n5. Проверяю CORS заголовки...")
        execute_ssh_command(
            ssh,
            "curl -s -H 'Origin: http://72.56.79.153' -H 'Access-Control-Request-Method: POST' -H 'Access-Control-Request-Headers: Content-Type' -X OPTIONS http://127.0.0.1:8000/api/auth/login -v 2>&1 | grep -i 'access-control'",
            "Проверка CORS заголовков"
        )
        
        # 6. Пересобираем frontend с новыми переменными окружения
        print("\n6. Пересобираю frontend с новыми переменными окружения...")
        execute_ssh_command(
            ssh,
            "cd /root/shannon/template && npm run build 2>&1 | tail -20",
            "Пересборка frontend"
        )
        
        # 7. Копируем обновленный dist в /var/www/shannon
        print("\n7. Копирую обновленный dist...")
        execute_ssh_command(
            ssh,
            "cp -r /root/shannon/template/dist/* /var/www/shannon/ && chown -R www-data:www-data /var/www/shannon && chmod -R 755 /var/www/shannon",
            "Копирование dist"
        )
        
        print("\n" + "="*60)
        print("ИСПРАВЛЕНИЕ ЗАВЕРШЕНО")
        print("="*60)
        print(f"\nFrontend: http://{SSH_HOST}/")
        print(f"Backend API: http://{SSH_HOST}/api/")
        print(f"WebSocket: ws://{SSH_HOST}/socket.io/")
        print("\nПроверьте работу приложения в браузере!")
        print("\nЕсли проблема сохраняется, проверьте:")
        print("1. Откройте консоль браузера (F12) и посмотрите ошибки")
        print("2. Проверьте Network tab для просмотра запросов")
        print("3. Убедитесь, что используете правильный URL: http://72.56.79.153/")
        
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

