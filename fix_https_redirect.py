#!/usr/bin/env python3
"""
Исправление редиректа на HTTPS - либо убираем, либо настраиваем SSL
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
    print("ИСПРАВЛЕНИЕ РЕДИРЕКТА НА HTTPS")
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
        # 1. Ищем все редиректы на HTTPS
        print("\n1. Ищу редиректы на HTTPS...")
        execute_ssh_command(
            ssh,
            "grep -r 'return 301' /etc/nginx/ 2>/dev/null | head -10",
            "Поиск редиректов 301"
        )
        
        execute_ssh_command(
            ssh,
            "grep -r 'return 302' /etc/nginx/ 2>/dev/null | head -10",
            "Поиск редиректов 302"
        )
        
        execute_ssh_command(
            ssh,
            "grep -r 'rewrite.*https' /etc/nginx/ 2>/dev/null | head -10",
            "Поиск rewrite на https"
        )
        
        execute_ssh_command(
            ssh,
            "grep -r 'ssl_redirect' /etc/nginx/ 2>/dev/null | head -10",
            "Поиск ssl_redirect"
        )
        
        # 2. Проверяем все конфигурации nginx
        print("\n2. Проверяю все конфигурации nginx...")
        execute_ssh_command(
            ssh,
            "cat /etc/nginx/nginx.conf | grep -A 10 'server {' | head -30",
            "Основная конфигурация nginx"
        )
        
        execute_ssh_command(
            ssh,
            "for file in /etc/nginx/sites-enabled/*; do echo '=== $file ==='; cat \"$file\" 2>/dev/null | grep -A 5 'return.*https\|rewrite.*https\|ssl_redirect'; done",
            "Проверка всех активных конфигураций"
        )
        
        # 3. Устанавливаем SSL сертификат (Let's Encrypt) или убираем редирект
        print("\n3. Выбираю решение: устанавливаю SSL или убираю редирект...")
        
        # Проверяем наличие certbot
        stdin, stdout, stderr = ssh.exec_command("which certbot || echo 'certbot not found'")
        certbot_available = 'certbot' in stdout.read().decode('utf-8', errors='replace')
        
        if certbot_available:
            print("Certbot найден. Можно установить SSL сертификат.")
            choice = "ssl"  # Можно установить SSL
        else:
            print("Certbot не найден. Убираю редирект на HTTPS.")
            choice = "remove"  # Убираем редирект
        
        # Для простоты убираем редирект (можно потом добавить SSL)
        choice = "remove"
        
        if choice == "remove":
            print("\n4. Убираю редиректы на HTTPS...")
            
            # Обновляем все конфигурации, убирая редиректы
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
        
        # Отключаем буферизацию
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
            
            if exit_status == 0:
                print("Конфигурация обновлена без редиректов!")
            
            # Убираем редиректы из других конфигураций если есть
            execute_ssh_command(
                ssh,
                "sed -i 's/return 301 https:\\/\\/\\$host\\$request_uri;//g' /etc/nginx/sites-available/* 2>/dev/null || true",
                "Удаление редиректов из других конфигураций"
            )
            
            execute_ssh_command(
                ssh,
                "sed -i 's/return 302 https:\\/\\/\\$host\\$request_uri;//g' /etc/nginx/sites-available/* 2>/dev/null || true",
                "Удаление редиректов 302"
            )
        
        # 5. Проверяем и перезапускаем nginx
        print("\n5. Проверяю и перезапускаю nginx...")
        execute_ssh_command(ssh, "nginx -t", "Проверка конфигурации nginx")
        execute_ssh_command(ssh, "systemctl reload nginx", "Перезагрузка nginx")
        
        # 6. Тестируем редиректы
        print("\n6. Тестирую редиректы...")
        execute_ssh_command(
            ssh,
            "curl -I http://72.56.79.153/ 2>&1 | grep -i 'location\|http' | head -5",
            "Проверка редиректов HTTP"
        )
        
        execute_ssh_command(
            ssh,
            "curl -I -k https://72.56.79.153/ 2>&1 | grep -i 'location\|http' | head -5",
            "Проверка редиректов HTTPS"
        )
        
        # 7. Финальная проверка
        print("\n7. Финальная проверка...")
        execute_ssh_command(
            ssh,
            "curl -v http://72.56.79.153/ 2>&1 | head -30",
            "Финальная проверка HTTP"
        )
        
        print("\n" + "="*60)
        print("ИСПРАВЛЕНИЕ ЗАВЕРШЕНО")
        print("="*60)
        print(f"\nHTTP: http://{SSH_HOST}/")
        print(f"Backend API: http://{SSH_HOST}/api/")
        print("\nРедиректы на HTTPS убраны.")
        print("Приложение доступно по HTTP без редиректов.")
        
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

