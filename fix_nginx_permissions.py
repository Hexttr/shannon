#!/usr/bin/env python3
"""
Скрипт для исправления прав доступа и конфигурации nginx
"""

import paramiko
import sys

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
FRONTEND_DIR = "/root/shannon/template"
DIST_DIR = f"{FRONTEND_DIR}/dist"

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
    print("ИСПРАВЛЕНИЕ ПРАВ ДОСТУПА И КОНФИГУРАЦИИ NGINX")
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
        # 1. Исправляем права доступа
        print("\n1. Исправляю права доступа...")
        execute_ssh_command(
            ssh,
            f"chmod -R 755 {FRONTEND_DIR} && chmod -R 755 {DIST_DIR}",
            "Установка прав доступа"
        )
        
        # 2. Устанавливаем правильного владельца (nginx обычно работает от www-data)
        execute_ssh_command(
            ssh,
            f"chown -R www-data:www-data {DIST_DIR} || chown -R nginx:nginx {DIST_DIR} || true",
            "Установка владельца"
        )
        
        # 3. Обновляем конфигурацию nginx с правильным proxy_pass
        print("\n2. Обновляю конфигурацию nginx...")
        nginx_config = f"""server {{
    listen 80;
    listen [::]:80;
    server_name 72.56.79.153;
    
    root {DIST_DIR};
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
    
    # Проксирование API запросов к backend (убираем /api из пути)
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
    }}
}}
"""
        
        config_file = "/etc/nginx/sites-available/shannon"
        stdin, stdout, stderr = ssh.exec_command(f"cat > {config_file} << 'NGINX_EOF'\n{nginx_config}\nNGINX_EOF\n")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            print("Ошибка при создании конфигурации nginx", file=sys.stderr)
            sys.exit(1)
        
        # 4. Проверяем и перезапускаем nginx
        print("\n3. Проверяю и перезапускаю nginx...")
        execute_ssh_command(ssh, "nginx -t", "Проверка конфигурации nginx")
        execute_ssh_command(ssh, "systemctl reload nginx", "Перезагрузка nginx")
        
        # 5. Финальная проверка
        print("\n4. Финальная проверка...")
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

