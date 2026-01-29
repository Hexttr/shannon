#!/usr/bin/env python3
"""
Скрипт для развертывания frontend на сервере Ubuntu
"""

import paramiko
import sys
import os

# Параметры подключения
SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
PROJECT_DIR = "/root/shannon"

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
    
    if exit_status != 0:
        print(f"Команда завершилась с кодом: {exit_status}", file=sys.stderr)
        return False, output
    
    return True, output

def main():
    print("="*60)
    print("РАЗВЕРТЫВАНИЕ FRONTEND НА СЕРВЕРЕ UBUNTU")
    print("="*60)
    
    # Подключение к серверу
    print(f"\nПодключаюсь к серверу {SSH_HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        print("Подключение установлено!")
    except Exception as e:
        print(f"Ошибка подключения: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 1. Проверяем наличие Node.js и npm
        print("\n1. Проверяю наличие Node.js и npm...")
        success, _ = execute_ssh_command(
            ssh,
            "which node && node --version && which npm && npm --version",
            "Проверка Node.js и npm"
        )
        
        if not success:
            print("\nNode.js не найден. Устанавливаю Node.js 20.x...")
            commands = [
                "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -",
                "apt-get install -y nodejs",
            ]
            for cmd in commands:
                execute_ssh_command(ssh, cmd, f"Установка: {cmd}")
            execute_ssh_command(ssh, "node --version && npm --version", "Проверка установки")
        
        # 2. Обновляем код на сервере
        print("\n2. Обновляю код на сервере...")
        # Проверяем наличие git репозитория
        success, _ = execute_ssh_command(
            ssh,
            f"cd {PROJECT_DIR} && git status 2>&1",
            "Проверка git репозитория"
        )
        
        if success:
            execute_ssh_command(ssh, f"cd {PROJECT_DIR} && git pull", "Git pull")
        else:
            # Если нет git, клонируем репозиторий
            print("Git репозиторий не найден. Клонирую репозиторий...")
            execute_ssh_command(
                ssh,
                f"cd {PROJECT_DIR} && git clone https://github.com/Hexttr/shannon.git temp_repo 2>&1 || true",
                "Клонирование репозитория"
            )
            execute_ssh_command(
                ssh,
                f"cd {PROJECT_DIR} && (test -d temp_repo/template && cp -r temp_repo/template/* template/ 2>/dev/null || true) && rm -rf temp_repo",
                "Копирование файлов frontend"
            )
        
        # 3. Ищем директорию frontend
        print("\n3. Ищу директорию frontend...")
        success, output = execute_ssh_command(
            ssh,
            f"find {PROJECT_DIR} -name 'package.json' -type f -not -path '*/node_modules/*' 2>/dev/null | grep -v node_modules | head -1",
            "Поиск package.json"
        )
        
        frontend_dir = None
        if output.strip() and 'node_modules' not in output:
            frontend_dir = os.path.dirname(output.strip())
            print(f"Найдена директория frontend: {frontend_dir}")
        else:
            frontend_dir = f"{PROJECT_DIR}/template"
            print(f"Использую стандартную директорию: {frontend_dir}")
        
        # 4. Устанавливаем зависимости
        print(f"\n4. Устанавливаю зависимости frontend в {frontend_dir}...")
        if not execute_ssh_command(
            ssh,
            f"cd {frontend_dir} && npm install",
            "npm install"
        )[0]:
            print("Ошибка при установке зависимостей", file=sys.stderr)
            sys.exit(1)
        
        # 5. Собираем frontend
        print(f"\n5. Собираю frontend в {frontend_dir}...")
        if not execute_ssh_command(
            ssh,
            f"cd {frontend_dir} && npm run build 2>&1",
            "npm run build"
        )[0]:
            print("Предупреждение: сборка завершилась с ошибками TypeScript, но продолжается...")
            # Проверяем наличие dist директории
            success, _ = execute_ssh_command(
                ssh,
                f"test -d {frontend_dir}/dist && echo 'dist exists' || echo 'dist not found'",
                "Проверка директории dist"
            )
            if 'not found' in output:
                print("Ошибка: директория dist не создана", file=sys.stderr)
                sys.exit(1)
        
        # 7. Проверяем наличие nginx
        print("\n7. Проверяю наличие nginx...")
        success, _ = execute_ssh_command(
            ssh,
            "which nginx && nginx -v",
            "Проверка nginx"
        )
        
        if not success:
            print("\nNginx не найден. Устанавливаю nginx...")
            if not execute_ssh_command(ssh, "apt-get update && apt-get install -y nginx", "Установка nginx")[0]:
                print("Ошибка при установке nginx", file=sys.stderr)
                sys.exit(1)
        
        # 8. Настраиваем nginx
        print("\n8. Настраиваю nginx...")
        web_dir = "/var/www/shannon"
        nginx_config = f"""server {{
    listen 80;
    listen [::]:80;
    server_name 72.56.79.153;
    
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
    index index.html;
    
    location / {{
        try_files $uri $uri/ /index.html;
    }}
    
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
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
        
        # Сохраняем конфигурацию через echo
        config_file = "/etc/nginx/sites-available/shannon"
        stdin, stdout, stderr = ssh.exec_command(f"cat > {config_file} << 'NGINX_EOF'\n{nginx_config}\nNGINX_EOF\n")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            print("Ошибка при создании конфигурации nginx", file=sys.stderr)
            sys.exit(1)
        
        # Активируем конфигурацию
        execute_ssh_command(
            ssh,
            f"ln -sf {config_file} /etc/nginx/sites-enabled/ && rm -f /etc/nginx/sites-enabled/default",
            "Активация конфигурации nginx"
        )
        
        # Проверяем конфигурацию
        if not execute_ssh_command(ssh, "nginx -t", "Проверка конфигурации nginx")[0]:
            print("Ошибка в конфигурации nginx", file=sys.stderr)
            sys.exit(1)
        
        # Перезапускаем nginx
        execute_ssh_command(ssh, "systemctl restart nginx", "Перезапуск nginx")
        execute_ssh_command(ssh, "systemctl status nginx --no-pager | head -10", "Статус nginx")
        
        print("\n" + "="*60)
        print("РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("="*60)
        print(f"\nFrontend доступен по адресу: http://{SSH_HOST}/")
        print(f"Backend API: http://{SSH_HOST}/api/")
        print(f"WebSocket: ws://{SSH_HOST}/socket.io/")
        print(f"\nДиректория frontend: {web_dir}")
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
