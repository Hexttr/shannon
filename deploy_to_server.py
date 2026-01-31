#!/usr/bin/env python3
"""
Полное развертывание приложения на сервере
Устанавливает зависимости и развертывает Laravel Backend + Frontend
"""

import paramiko
import os
from pathlib import Path

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
BACKEND_DIR = "/root/shannon/backend-laravel"
FRONTEND_DIR = "/root/shannon/template"

def ssh_exec(ssh, command, description=""):
    """Выполняет команду на сервере и выводит результат"""
    if description:
        print(f"  {description}...")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    
    if exit_status != 0 and error:
        print(f"    [WARNING] {error[:200]}")
    
    return output, exit_status

def main():
    print("="*60)
    print("ПОЛНОЕ РАЗВЕРТЫВАНИЕ НА СЕРВЕРЕ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка и установка PHP
        print("\n1. УСТАНОВКА PHP:")
        stdin, stdout, stderr = ssh.exec_command("php -v 2>&1")
        php_check = stdout.read().decode('utf-8', errors='replace')
        
        if "PHP" not in php_check:
            print("  PHP не установлен, устанавливаем...")
            ssh_exec(ssh, "apt-get update", "Обновление пакетов")
            ssh_exec(ssh, "apt-get install -y php8.2 php8.2-cli php8.2-fpm php8.2-mbstring php8.2-xml php8.2-curl php8.2-sqlite3 php8.2-zip php8.2-gd php8.2-bcmath", "Установка PHP и расширений")
        else:
            print(f"  [OK] PHP уже установлен: {php_check.split(chr(10))[0]}")
        
        # 2. Проверка и установка Composer
        print("\n2. УСТАНОВКА COMPOSER:")
        stdin, stdout, stderr = ssh.exec_command("composer --version 2>&1")
        composer_check = stdout.read().decode('utf-8', errors='replace')
        
        if "Composer" not in composer_check:
            print("  Composer не установлен, устанавливаем...")
            ssh_exec(ssh, "curl -sS https://getcomposer.org/installer | php && mv composer.phar /usr/local/bin/composer && chmod +x /usr/local/bin/composer", "Установка Composer")
        else:
            print(f"  [OK] Composer уже установлен: {composer_check.split(chr(10))[0]}")
        
        # 3. Проверка и установка Node.js
        print("\n3. УСТАНОВКА NODE.JS:")
        stdin, stdout, stderr = ssh.exec_command("node --version 2>&1")
        node_check = stdout.read().decode('utf-8', errors='replace')
        
        if "v" not in node_check:
            print("  Node.js не установлен, устанавливаем...")
            ssh_exec(ssh, "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -", "Добавление репозитория Node.js")
            ssh_exec(ssh, "apt-get install -y nodejs", "Установка Node.js")
        else:
            print(f"  [OK] Node.js уже установлен: {node_check.strip()}")
        
        # 4. Клонирование/обновление репозитория
        print("\n4. ОБНОВЛЕНИЕ РЕПОЗИТОРИЯ:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon && git pull 2>&1 || (git clone https://github.com/Hexttr/shannon.git /root/shannon 2>&1)")
        output = stdout.read().decode('utf-8', errors='replace')
        print("  [OK] Репозиторий обновлен")
        
        # 5. Развертывание Laravel Backend
        print("\n5. РАЗВЕРТЫВАНИЕ LARAVEL BACKEND:")
        ssh_exec(ssh, f"mkdir -p {BACKEND_DIR}", "Создание директории")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && composer install --no-dev --optimize-autoloader 2>&1", "Установка зависимостей")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && [ ! -f .env ] && cp .env.example .env || echo 'exists'", "Настройка .env")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan key:generate --force 2>&1", "Генерация APP_KEY")
        
        # Настройка базы данных в .env
        ssh_exec(ssh, f"cd {BACKEND_DIR} && sed -i 's/DB_CONNECTION=.*/DB_CONNECTION=sqlite/' .env", "Настройка БД")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && sed -i 's|DB_DATABASE=.*|DB_DATABASE={BACKEND_DIR}/database/database.sqlite|' .env", "Настройка пути к БД")
        
        ssh_exec(ssh, f"cd {BACKEND_DIR} && touch database/database.sqlite", "Создание БД")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan migrate --force 2>&1", "Запуск миграций")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && chmod -R 775 storage bootstrap/cache", "Настройка прав")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan config:cache 2>&1", "Кэширование конфигурации")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan route:cache 2>&1", "Кэширование маршрутов")
        
        # 6. Создание systemd service
        print("\n6. СОЗДАНИЕ SYSTEMD SERVICE:")
        service_content = f"""[Unit]
Description=Shannon Laravel Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={BACKEND_DIR}
ExecStart=/usr/bin/php {BACKEND_DIR}/artisan serve --host=0.0.0.0 --port=8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        stdin, stdout, stderr = ssh.exec_command(f"cat > /etc/systemd/system/shannon-laravel.service << 'EOFSERVICE'\n{service_content}\nEOFSERVICE")
        ssh_exec(ssh, "systemctl daemon-reload", "Перезагрузка systemd")
        ssh_exec(ssh, "systemctl enable shannon-laravel.service", "Включение автозапуска")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service", "Запуск сервиса")
        
        # Проверка статуса
        stdin, stdout, stderr = ssh.exec_command("systemctl status shannon-laravel.service --no-pager -l | head -20")
        status = stdout.read().decode('utf-8', errors='replace')
        if "active (running)" in status.lower():
            print("  [OK] Сервис запущен и работает")
        else:
            print("  [WARNING] Проверьте статус сервиса вручную")
        
        # 7. Развертывание Frontend
        print("\n7. РАЗВЕРТЫВАНИЕ FRONTEND:")
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && cat > .env << 'EOFFRONTEND'\nVITE_API_URL=https://{SSH_HOST}/api\nEOFFRONTEND", "Создание .env")
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && npm install 2>&1", "Установка зависимостей")
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && npm run build 2>&1", "Сборка frontend")
        
        # 8. Настройка Nginx
        print("\n8. НАСТРОЙКА NGINX:")
        nginx_config = f"""server {{
    listen 80;
    listen [::]:80;
    server_name {SSH_HOST};

    root {FRONTEND_DIR}/dist;
    index index.html;

    location / {{
        try_files $uri $uri/ /index.html;
    }}

    location /api {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    location /up {{
        proxy_pass http://127.0.0.1:8000/up;
        proxy_set_header Host $host;
    }}
}}
"""
        
        stdin, stdout, stderr = ssh.exec_command(f"cat > /etc/nginx/sites-available/shannon << 'EOFNGINX'\n{nginx_config}\nEOFNGINX")
        ssh_exec(ssh, "ln -sf /etc/nginx/sites-available/shannon /etc/nginx/sites-enabled/shannon", "Активация конфигурации")
        ssh_exec(ssh, "rm -f /etc/nginx/sites-enabled/default", "Удаление default конфигурации")
        stdin, stdout, stderr = ssh.exec_command("nginx -t 2>&1")
        nginx_test = stdout.read().decode('utf-8', errors='replace')
        if "successful" in nginx_test.lower():
            ssh_exec(ssh, "systemctl reload nginx", "Перезагрузка Nginx")
            print("  [OK] Nginx настроен и перезагружен")
        else:
            print(f"  [ERROR] Ошибка конфигурации Nginx: {nginx_test}")
        
        print("\n" + "="*60)
        print("РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!")
        print("="*60)
        print(f"\nПриложение доступно на: http://{SSH_HOST}")
        print(f"\nСОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ:")
        print(f"  ssh {SSH_USER}@{SSH_HOST}")
        print(f"  cd {BACKEND_DIR}")
        print(f"  php artisan tinker")
        print(f"  \\App\\Models\\User::create([")
        print(f"    'id' => \\Illuminate\\Support\\Str::uuid(),")
        print(f"    'username' => 'admin',")
        print(f"    'email' => 'admin@test.com',")
        print(f"    'password' => \\Illuminate\\Support\\Facades\\Hash::make('admin'),")
        print(f"  ]);")
        print(f"\nПРОВЕРКА:")
        print(f"  - Backend: curl http://{SSH_HOST}/api/auth/login")
        print(f"  - Frontend: http://{SSH_HOST}")
        print(f"  - Логи backend: journalctl -u shannon-laravel -f")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

