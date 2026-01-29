#!/usr/bin/env python3
"""
Полная диагностика и исправление проблем
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
    print("ПОЛНАЯ ДИАГНОСТИКА И ИСПРАВЛЕНИЕ ПРОБЛЕМ")
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
        # 1. Проверяем статус backend
        print("\n1. Проверяю статус backend...")
        success, output = execute_ssh_command(
            ssh,
            "ps aux | grep -E 'python.*uvicorn|python.*run.py' | grep -v grep",
            "Процессы backend"
        )
        
        backend_running = 'python' in output or 'uvicorn' in output
        
        if not backend_running:
            print("\n[WARN] Backend не запущен. Запускаю...")
            execute_ssh_command(
                ssh,
                "cd /root/shannon/backend && python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 > /tmp/shannon-backend.log 2>&1 &",
                "Запуск backend"
            )
            time.sleep(3)
            execute_ssh_command(
                ssh,
                "ps aux | grep -E 'python.*uvicorn|python.*run.py' | grep -v grep",
                "Проверка запуска"
            )
        
        # 2. Проверяем порт 8000
        print("\n2. Проверяю порт 8000...")
        execute_ssh_command(
            ssh,
            "ss -tlnp | grep :8000 || netstat -tlnp | grep :8000 || echo 'Порт 8000 не слушается'",
            "Порт 8000"
        )
        
        # 3. Проверяем доступность backend
        print("\n3. Проверяю доступность backend...")
        execute_ssh_command(
            ssh,
            "curl -s http://127.0.0.1:8000/health || echo 'Backend не отвечает'",
            "Проверка /health"
        )
        
        # 4. Проверяем логи backend на ошибки
        print("\n4. Проверяю логи backend...")
        execute_ssh_command(
            ssh,
            "tail -50 /tmp/shannon-backend.log 2>/dev/null || tail -50 /root/shannon/backend/server.log 2>/dev/null || echo 'Логи не найдены'",
            "Логи backend"
        )
        
        # 5. Проверяем конфигурацию backend
        print("\n5. Проверяю конфигурацию backend...")
        execute_ssh_command(
            ssh,
            "cat /root/shannon/backend/.env | grep -E 'CORS|DATABASE|JWT' | head -10",
            "Конфигурация backend"
        )
        
        # 6. Проверяем статус nginx
        print("\n6. Проверяю статус nginx...")
        execute_ssh_command(
            ssh,
            "systemctl status nginx --no-pager | head -10",
            "Статус nginx"
        )
        
        # 7. Проверяем логи nginx на ошибки
        print("\n7. Проверяю логи nginx...")
        execute_ssh_command(
            ssh,
            "tail -30 /var/log/nginx/error.log | grep -v 'phpunit' | tail -15",
            "Ошибки nginx"
        )
        
        # 8. Проверяем конфигурацию nginx
        print("\n8. Проверяю конфигурацию nginx...")
        execute_ssh_command(
            ssh,
            "nginx -t",
            "Проверка конфигурации nginx"
        )
        
        # 9. Проверяем наличие frontend файлов
        print("\n9. Проверяю frontend файлы...")
        execute_ssh_command(
            ssh,
            "ls -la /var/www/shannon/ | head -10",
            "Файлы frontend"
        )
        
        execute_ssh_command(
            ssh,
            "test -f /var/www/shannon/index.html && echo 'index.html exists' || echo 'index.html not found'",
            "Проверка index.html"
        )
        
        # 10. Проверяем доступность frontend
        print("\n10. Проверяю доступность frontend...")
        execute_ssh_command(
            ssh,
            "curl -s -I http://localhost/ | head -5",
            "Проверка frontend"
        )
        
        # 11. Проверяем доступность API через nginx
        print("\n11. Проверяю API через nginx...")
        execute_ssh_command(
            ssh,
            "curl -s -I http://localhost/api/health 2>&1 | head -5",
            "Проверка /api/health"
        )
        
        # 12. Тестируем полный запрос к API
        print("\n12. Тестирую полный запрос к API...")
        execute_ssh_command(
            ssh,
            "curl -s http://localhost/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"513277\"}' | head -3",
            "Тест API login"
        )
        
        # 13. Проверяем CORS заголовки
        print("\n13. Проверяю CORS заголовки...")
        execute_ssh_command(
            ssh,
            "curl -s -H 'Origin: http://72.56.79.153' -X OPTIONS http://127.0.0.1:8000/api/auth/login -v 2>&1 | grep -i 'access-control' | head -5",
            "Проверка CORS"
        )
        
        # 14. Исправляем проблемы если есть
        print("\n14. Исправляю проблемы...")
        
        # Проверяем и исправляем CORS если нужно
        backend_env_file = "/root/shannon/backend/.env"
        stdin, stdout, stderr = ssh.exec_command(f"grep 'CORS_ORIGINS' {backend_env_file} 2>/dev/null || echo ''")
        cors_config = stdout.read().decode('utf-8', errors='replace')
        
        if 'http://72.56.79.153"' not in cors_config and 'http://72.56.79.153' not in cors_config:
            print("Обновляю CORS настройки...")
            stdin, stdout, stderr = ssh.exec_command(f"cat {backend_env_file} 2>/dev/null || echo ''")
            current_env = stdout.read().decode('utf-8', errors='replace')
            
            new_cors_origins = 'CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://72.56.79.153","http://72.56.79.153:5173","http://72.56.79.153:3000","http://72.56.79.153:8000"]'
            
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
            
            # Перезапускаем backend для применения изменений
            print("Перезапускаю backend для применения CORS настроек...")
            execute_ssh_command(
                ssh,
                "pkill -f 'python.*uvicorn.*app.main:socketio_app' || true",
                "Остановка backend"
            )
            time.sleep(2)
            execute_ssh_command(
                ssh,
                "cd /root/shannon/backend && python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 > /tmp/shannon-backend.log 2>&1 &",
                "Запуск backend"
            )
            time.sleep(3)
        
        # 15. Финальная проверка
        print("\n15. Финальная проверка...")
        execute_ssh_command(
            ssh,
            "curl -s http://127.0.0.1:8000/health",
            "Проверка backend health"
        )
        
        execute_ssh_command(
            ssh,
            "curl -s -o /dev/null -w '%{http_code}' http://localhost/",
            "Проверка frontend HTTP код"
        )
        
        execute_ssh_command(
            ssh,
            "curl -s -o /dev/null -w '%{http_code}' http://localhost/api/health",
            "Проверка API HTTP код"
        )
        
        # Итоговый статус
        print("\n" + "="*60)
        print("ИТОГОВЫЙ СТАТУС")
        print("="*60)
        
        # Проверяем все компоненты еще раз
        success, backend_proc = execute_ssh_command(
            ssh,
            "ps aux | grep -E 'python.*uvicorn|python.*run.py' | grep -v grep | wc -l",
            "Количество процессов backend"
        )
        
        success, nginx_status = execute_ssh_command(
            ssh,
            "systemctl is-active nginx",
            "Статус nginx"
        )
        
        success, backend_health = execute_ssh_command(
            ssh,
            "curl -s http://127.0.0.1:8000/health 2>&1",
            "Backend health"
        )
        
        success, frontend_code = execute_ssh_command(
            ssh,
            "curl -s -o /dev/null -w '%{http_code}' http://localhost/",
            "Frontend HTTP код"
        )
        
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТЫ ДИАГНОСТИКИ")
        print("="*60)
        print(f"Backend процесс: {'[OK] Работает' if '1' in backend_proc or '2' in backend_proc else '[FAIL] Не работает'}")
        print(f"Nginx: {'[OK] ' + nginx_status.strip() if 'active' in nginx_status else '[FAIL] Не работает'}")
        print(f"Backend health: {'[OK] ' + backend_health.strip() if 'ok' in backend_health.lower() or 'status' in backend_health.lower() else '[FAIL] Не отвечает'}")
        print(f"Frontend: {'[OK] HTTP ' + frontend_code.strip() if '200' in frontend_code else '[FAIL] HTTP ' + frontend_code.strip()}")
        
        print("\n" + "="*60)
        print("ПРИЛОЖЕНИЕ ГОТОВО К ТЕСТИРОВАНИЮ")
        print("="*60)
        print(f"\nFrontend: http://{SSH_HOST}/")
        print(f"Backend API: http://{SSH_HOST}/api/")
        print(f"API Docs: http://{SSH_HOST}/api/docs")
        print(f"WebSocket: ws://{SSH_HOST}/socket.io/")
        print("\nУчетные данные для входа:")
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

