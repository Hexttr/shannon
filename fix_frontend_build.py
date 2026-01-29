#!/usr/bin/env python3
"""
Скрипт для пересборки frontend и исправления конфигурации nginx
"""

import paramiko
import sys
import os

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
    print("ПЕРЕСБОРКА FRONTEND И ИСПРАВЛЕНИЕ NGINX")
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
        # 1. Проверяем наличие других конфигураций nginx
        print("\n1. Проверяю другие конфигурации nginx...")
        execute_ssh_command(ssh, "ls -la /etc/nginx/sites-enabled/", "Активные конфигурации nginx")
        execute_ssh_command(ssh, "grep -r 'server_name.*72.56.79.153' /etc/nginx/ 2>/dev/null | head -10", "Поиск конфликтующих конфигураций")
        
        # 2. Обновляем код
        print("\n2. Обновляю код...")
        execute_ssh_command(ssh, f"cd {PROJECT_DIR} && git pull", "Git pull")
        
        # 3. Пересобираем frontend
        print("\n3. Пересобираю frontend...")
        execute_ssh_command(ssh, f"cd {FRONTEND_DIR} && rm -rf dist node_modules/.vite", "Очистка старых файлов")
        execute_ssh_command(ssh, f"cd {FRONTEND_DIR} && npm install", "Установка зависимостей")
        execute_ssh_command(ssh, f"cd {FRONTEND_DIR} && npm run build 2>&1 | tail -50", "Сборка frontend")
        
        # 4. Проверяем наличие dist
        print("\n4. Проверяю наличие dist...")
        success, output = execute_ssh_command(
            ssh,
            f"test -d {FRONTEND_DIR}/dist && ls -la {FRONTEND_DIR}/dist/ | head -10 || echo 'dist не найден'",
            "Проверка dist"
        )
        
        if 'не найден' in output:
            print("ОШИБКА: dist не создан!", file=sys.stderr)
            # Проверяем ошибки сборки
            execute_ssh_command(ssh, f"cd {FRONTEND_DIR} && npm run build 2>&1", "Повторная сборка с выводом ошибок")
            sys.exit(1)
        
        # 5. Отключаем другие конфигурации
        print("\n5. Отключаю конфликтующие конфигурации...")
        execute_ssh_command(ssh, "ls /etc/nginx/sites-enabled/ | grep -v shannon | xargs -I {} rm -f /etc/nginx/sites-enabled/{} 2>/dev/null || true", "Удаление других конфигураций")
        
        # 6. Обновляем конфигурацию nginx
        print("\n6. Обновляю конфигурацию nginx...")
        dist_dir = f"{FRONTEND_DIR}/dist"
        nginx_config = f"""server {{
    listen 80;
    listen [::]:80;
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
        
        if exit_status != 0:
            print("Ошибка при создании конфигурации nginx", file=sys.stderr)
            sys.exit(1)
        
        # 7. Активируем конфигурацию
        execute_ssh_command(ssh, f"ln -sf {config_file} /etc/nginx/sites-enabled/shannon", "Активация конфигурации")
        
        # 8. Проверяем и перезапускаем nginx
        print("\n8. Проверяю и перезапускаю nginx...")
        execute_ssh_command(ssh, "nginx -t", "Проверка конфигурации nginx")
        execute_ssh_command(ssh, "systemctl reload nginx", "Перезагрузка nginx")
        
        # 9. Финальная проверка
        print("\n9. Финальная проверка...")
        execute_ssh_command(ssh, "curl -s -I http://localhost/ | head -5", "Проверка frontend")
        execute_ssh_command(ssh, "curl -s -I http://localhost/api/docs | head -5", "Проверка API")
        
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

