#!/usr/bin/env python3
"""
Скрипт для диагностики и исправления проблем развертывания
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
    print("ДИАГНОСТИКА И ИСПРАВЛЕНИЕ ПРОБЛЕМ РАЗВЕРТЫВАНИЯ")
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
        execute_ssh_command(ssh, "ps aux | grep -E 'python.*run.py|uvicorn' | grep -v grep", "Процессы backend")
        execute_ssh_command(ssh, "netstat -tlnp | grep :8000 || ss -tlnp | grep :8000", "Порт 8000")
        
        # 2. Проверяем доступность backend
        print("\n2. Проверяю доступность backend...")
        success, output = execute_ssh_command(
            ssh,
            "curl -s http://localhost:8000/docs || curl -s http://localhost:8000/ || echo 'Backend не отвечает'",
            "Проверка backend на localhost:8000"
        )
        
        # 3. Запускаем backend если не запущен
        if 'не отвечает' in output or not success:
            print("\n3. Backend не запущен. Запускаю backend...")
            execute_ssh_command(
                ssh,
                "cd /root/shannon/backend && source venv/bin/activate && nohup python run.py > /tmp/shannon-backend.log 2>&1 &",
                "Запуск backend"
            )
            import time
            time.sleep(3)
            execute_ssh_command(ssh, "ps aux | grep -E 'python.*run.py' | grep -v grep", "Проверка запуска backend")
        
        # 4. Проверяем конфигурацию nginx
        print("\n4. Проверяю конфигурацию nginx...")
        success, nginx_config = execute_ssh_command(
            ssh,
            "cat /etc/nginx/sites-available/shannon",
            "Конфигурация nginx"
        )
        
        # 5. Проверяем наличие dist директории
        print("\n5. Проверяю наличие dist директории...")
        execute_ssh_command(
            ssh,
            "ls -la /root/shannon/template/dist/ | head -10",
            "Содержимое dist"
        )
        
        # 6. Проверяем логи nginx
        print("\n6. Проверяю логи nginx...")
        execute_ssh_command(
            ssh,
            "tail -20 /var/log/nginx/error.log",
            "Последние ошибки nginx"
        )
        
        # 7. Исправляем конфигурацию nginx если нужно
        print("\n7. Обновляю конфигурацию nginx...")
        frontend_dir = "/root/shannon/template"
        dist_dir = f"{frontend_dir}/dist"
        
        nginx_config = f"""server {{
    listen 80;
    server_name 72.56.79.153;
    
    root {dist_dir};
    index index.html;
    
    # Раздача статических файлов
    location / {{
        try_files $uri $uri/ /index.html;
    }}
    
    # Кэширование статических ресурсов
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # Проксирование API запросов к backend
    location /api {{
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }}
    
    # Проксирование WebSocket для Socket.IO
    location /socket.io {{
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        
        config_file = "/etc/nginx/sites-available/shannon"
        stdin, stdout, stderr = ssh.exec_command(f"cat > {config_file} << 'NGINX_EOF'\n{nginx_config}\nNGINX_EOF\n")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Конфигурация nginx обновлена!")
        
        # 8. Проверяем конфигурацию и перезапускаем nginx
        print("\n8. Проверяю и перезапускаю nginx...")
        execute_ssh_command(ssh, "nginx -t", "Проверка конфигурации nginx")
        execute_ssh_command(ssh, "systemctl restart nginx", "Перезапуск nginx")
        execute_ssh_command(ssh, "systemctl status nginx --no-pager | head -10", "Статус nginx")
        
        # 9. Финальная проверка
        print("\n9. Финальная проверка...")
        execute_ssh_command(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/", "Проверка frontend")
        execute_ssh_command(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost/api/docs", "Проверка API")
        
        print("\n" + "="*60)
        print("ДИАГНОСТИКА ЗАВЕРШЕНА!")
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

