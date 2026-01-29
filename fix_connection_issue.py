#!/usr/bin/env python3
"""
Скрипт для диагностики и исправления ERR_CONNECTION_CLOSED
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
    print("ДИАГНОСТИКА ERR_CONNECTION_CLOSED")
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
        # 1. Проверяем доступность backend напрямую
        print("\n1. Проверяю доступность backend напрямую...")
        execute_ssh_command(
            ssh,
            "curl -v http://127.0.0.1:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"513277\"}' 2>&1 | head -20",
            "Проверка backend API напрямую"
        )
        
        # 2. Проверяем доступность через nginx
        print("\n2. Проверяю доступность через nginx...")
        execute_ssh_command(
            ssh,
            "curl -v http://localhost/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"513277\"}' 2>&1 | head -20",
            "Проверка через nginx"
        )
        
        # 3. Проверяем конфигурацию nginx
        print("\n3. Проверяю конфигурацию nginx...")
        execute_ssh_command(
            ssh,
            "cat /etc/nginx/sites-available/shannon",
            "Конфигурация nginx"
        )
        
        # 4. Проверяем логи nginx
        print("\n4. Проверяю логи nginx...")
        execute_ssh_command(
            ssh,
            "tail -30 /var/log/nginx/error.log | grep -v 'phpunit' | tail -10",
            "Последние ошибки nginx"
        )
        
        execute_ssh_command(
            ssh,
            "tail -20 /var/log/nginx/access.log | tail -10",
            "Последние запросы nginx"
        )
        
        # 5. Проверяем переменные окружения frontend
        print("\n5. Проверяю переменные окружения frontend...")
        execute_ssh_command(
            ssh,
            "cat /root/shannon/template/.env 2>/dev/null || echo '.env не найден'",
            "Переменные окружения frontend"
        )
        
        # 6. Проверяем содержимое index.html на наличие правильных URL
        print("\n6. Проверяю index.html на наличие правильных URL...")
        execute_ssh_command(
            ssh,
            "grep -o 'http://[^\" ]*' /var/www/shannon/index.html | head -5",
            "URL в index.html"
        )
        
        # 7. Проверяем CORS настройки backend
        print("\n7. Проверяю CORS настройки backend...")
        execute_ssh_command(
            ssh,
            "grep -A 5 'cors_origins' /root/shannon/backend/.env 2>/dev/null || grep -A 5 'CORS_ORIGINS' /root/shannon/backend/.env 2>/dev/null || echo 'CORS настройки не найдены в .env'",
            "CORS настройки"
        )
        
        # 8. Исправляем конфигурацию nginx с правильными таймаутами
        print("\n8. Обновляю конфигурацию nginx с правильными таймаутами...")
        web_dir = "/var/www/shannon"
        nginx_config = f"""server {{
    listen 80;
    listen [::]:80;
    server_name 72.56.79.153;
    
    root {web_dir};
    index index.html;
    
    # Увеличиваем размер буферов
    client_max_body_size 100M;
    client_body_buffer_size 128k;
    
    # Таймауты
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
    send_timeout 300s;
    
    # Раздача статических файлов
    location / {{
        try_files $uri $uri/ /index.html;
    }}
    
    # Кэширование статических ресурсов
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }}
    
    # Проксирование API запросов к backend
    location /api {{
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Таймауты для прокси
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Отключаем буферизацию для streaming ответов
        proxy_buffering off;
    }}
    
    # Проксирование WebSocket для Socket.IO
    location /socket.io {{
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Таймауты для WebSocket
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }}
}}
"""
        
        config_file = "/etc/nginx/sites-available/shannon"
        stdin, stdout, stderr = ssh.exec_command(f"cat > {config_file} << 'NGINX_EOF'\n{nginx_config}\nNGINX_EOF\n")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            print("Ошибка при создании конфигурации nginx", file=sys.stderr)
            sys.exit(1)
        
        # 9. Проверяем и перезапускаем nginx
        print("\n9. Проверяю и перезапускаю nginx...")
        execute_ssh_command(ssh, "nginx -t", "Проверка конфигурации nginx")
        execute_ssh_command(ssh, "systemctl reload nginx", "Перезагрузка nginx")
        
        # 10. Финальная проверка
        print("\n10. Финальная проверка...")
        execute_ssh_command(
            ssh,
            "curl -s -I http://localhost/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"513277\"}' | head -5",
            "Проверка API через nginx"
        )
        
        print("\n" + "="*60)
        print("ДИАГНОСТИКА ЗАВЕРШЕНА")
        print("="*60)
        print(f"\nFrontend: http://{SSH_HOST}/")
        print(f"Backend API: http://{SSH_HOST}/api/")
        print(f"WebSocket: ws://{SSH_HOST}/socket.io/")
        print("\nПроверьте работу приложения в браузере!")
        
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

