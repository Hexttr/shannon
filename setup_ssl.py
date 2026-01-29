#!/usr/bin/env python3
"""
Настройка SSL сертификата через Let's Encrypt
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
    print("НАСТРОЙКА SSL СЕРТИФИКАТА")
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
        # 1. Проверяем наличие certbot
        print("\n1. Проверяю наличие certbot...")
        success, output = execute_ssh_command(
            ssh,
            "which certbot || echo 'certbot not found'",
            "Проверка certbot"
        )
        
        certbot_installed = 'certbot' in output and 'not found' not in output
        
        # 2. Устанавливаем certbot если нужно
        if not certbot_installed:
            print("\n2. Устанавливаю certbot...")
            execute_ssh_command(
                ssh,
                "apt-get update && apt-get install -y certbot python3-certbot-nginx",
                "Установка certbot"
            )
        
        # 3. Получаем SSL сертификат
        print("\n3. Получаю SSL сертификат...")
        # Для IP адреса нужно использовать --standalone, так как Let's Encrypt не выдает сертификаты для IP
        # Но можно попробовать получить сертификат через DNS или использовать самоподписанный
        
        # Проверяем, есть ли домен или используем IP
        # Для IP адреса создадим самоподписанный сертификат или используем существующий
        
        # Проверяем существующие сертификаты
        execute_ssh_command(
            ssh,
            "ls -la /etc/ssl/certs/pentest.crt /etc/ssl/private/pentest.key 2>/dev/null && echo 'Существующие сертификаты найдены' || echo 'Сертификаты не найдены'",
            "Проверка существующих сертификатов"
        )
        
        # Используем существующие сертификаты или создаем новые
        cert_path = "/etc/ssl/certs/pentest.crt"
        key_path = "/etc/ssl/private/pentest.key"
        
        stdin, stdout, stderr = ssh.exec_command(f"test -f {cert_path} && test -f {key_path} && echo 'exists' || echo 'not exists'")
        certs_exist = 'exists' in stdout.read().decode('utf-8', errors='replace')
        
        if not certs_exist:
            print("\n4. Создаю самоподписанный SSL сертификат...")
            execute_ssh_command(
                ssh,
                f"mkdir -p /etc/ssl/certs /etc/ssl/private",
                "Создание директорий для сертификатов"
            )
            
            # Создаем самоподписанный сертификат
            execute_ssh_command(
                ssh,
                f"openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout {key_path} -out {cert_path} -subj '/CN=72.56.79.153' -addext 'subjectAltName=IP:72.56.79.153' 2>&1",
                "Создание самоподписанного сертификата"
            )
            
            execute_ssh_command(
                ssh,
                f"chmod 600 {key_path} && chmod 644 {cert_path}",
                "Установка прав на сертификаты"
            )
        else:
            print("\n4. Использую существующие сертификаты...")
        
        # 5. Настраиваем nginx для HTTPS
        print("\n5. Настраиваю nginx для HTTPS...")
        web_dir = "/var/www/shannon"
        
        nginx_config = f"""# HTTP сервер - редирект на HTTPS
server {{
    listen 80;
    listen [::]:80;
    server_name 72.56.79.153;
    
    # Редирект на HTTPS
    return 301 https://$server_name$request_uri;
}}

# HTTPS сервер
server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name 72.56.79.153;
    
    # SSL сертификаты
    ssl_certificate {cert_path};
    ssl_certificate_key {key_path};
    
    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Увеличиваем размер буферов
    client_max_body_size 100M;
    client_body_buffer_size 128k;
    
    # Таймауты
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
    send_timeout 300s;
    
    root {web_dir};
    index index.html;
    
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
            print("Конфигурация nginx с HTTPS создана!")
        
        # 6. Проверяем и перезапускаем nginx
        print("\n6. Проверяю и перезапускаю nginx...")
        execute_ssh_command(ssh, "nginx -t", "Проверка конфигурации nginx")
        execute_ssh_command(ssh, "systemctl reload nginx", "Перезагрузка nginx")
        
        # 7. Проверяем порт 443
        print("\n7. Проверяю порт 443...")
        execute_ssh_command(
            ssh,
            "ss -tlnp | grep :443 || netstat -tlnp | grep :443",
            "Порт 443"
        )
        
        # 8. Тестируем HTTPS
        print("\n8. Тестирую HTTPS...")
        execute_ssh_command(
            ssh,
            "curl -k -I https://localhost/ 2>&1 | head -10",
            "Проверка HTTPS на localhost"
        )
        
        execute_ssh_command(
            ssh,
            "curl -k -I https://72.56.79.153/ 2>&1 | head -10",
            "Проверка HTTPS по IP"
        )
        
        # 9. Тестируем редирект с HTTP на HTTPS
        print("\n9. Тестирую редирект HTTP -> HTTPS...")
        execute_ssh_command(
            ssh,
            "curl -I http://72.56.79.153/ 2>&1 | head -10",
            "Проверка редиректа"
        )
        
        # 10. Финальная проверка
        print("\n10. Финальная проверка...")
        execute_ssh_command(
            ssh,
            "curl -k -s https://72.56.79.153/ | head -15",
            "Проверка содержимого HTTPS"
        )
        
        print("\n" + "="*60)
        print("SSL НАСТРОЕН")
        print("="*60)
        print(f"\nHTTP: http://{SSH_HOST}/ (редирект на HTTPS)")
        print(f"HTTPS: https://{SSH_HOST}/")
        print(f"Backend API: https://{SSH_HOST}/api/")
        print(f"WebSocket: wss://{SSH_HOST}/socket.io/")
        print("\nПримечание: Используется самоподписанный сертификат.")
        print("Браузер может показать предупреждение о безопасности.")
        print("Это нормально для самоподписанных сертификатов.")
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

