#!/usr/bin/env python3
"""
Установка PHP и развертывание Laravel Backend на сервере
"""

import paramiko

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
BACKEND_DIR = "/root/shannon/backend-laravel"
FRONTEND_DIR = "/root/shannon/template"

def ssh_exec(ssh, command, description=""):
    """Выполняет команду на сервере"""
    if description:
        print(f"  {description}...")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    
    if exit_status != 0:
        if error:
            print(f"    [ERROR] {error[:300]}")
        return False, output + error
    return True, output

def main():
    print("="*60)
    print("УСТАНОВКА PHP И РАЗВЕРТЫВАНИЕ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Установка PHP
        print("\n1. УСТАНОВКА PHP:")
        success, output = ssh_exec(ssh, "php -v 2>&1", "Проверка PHP")
        
        if not success or "PHP" not in output:
            print("  Установка PHP...")
            ssh_exec(ssh, "apt-get update -y", "Обновление пакетов")
            
            # Проверяем доступные версии PHP
            success, output = ssh_exec(ssh, "apt-cache search php | grep -E '^php[0-9]' | head -5")
            print(f"  Доступные версии PHP: {output[:200]}")
            
            # Пробуем установить PHP (может быть php8.1, php8.3 или просто php)
            php_packages = [
                "php php-cli php-fpm php-mbstring php-xml php-curl php-sqlite3 php-zip php-gd php-bcmath",
                "php8.1 php8.1-cli php8.1-fpm php8.1-mbstring php8.1-xml php8.1-curl php8.1-sqlite3 php8.1-zip php8.1-gd php8.1-bcmath",
                "php8.3 php8.3-cli php8.3-fpm php8.3-mbstring php8.3-xml php8.3-curl php8.3-sqlite3 php8.3-zip php8.3-gd php8.3-bcmath",
            ]
            
            php_installed = False
            for packages in php_packages:
                success, output = ssh_exec(ssh, f"apt-get install -y {packages} 2>&1")
                if success:
                    php_installed = True
                    print(f"  [OK] PHP установлен: {packages.split()[0]}")
                    break
            
            if not php_installed:
                print("  [ERROR] Не удалось установить PHP")
                return
        else:
            print(f"  [OK] PHP уже установлен")
        
        # Проверка версии PHP
        success, output = ssh_exec(ssh, "php -v")
        print(f"  {output.split(chr(10))[0]}")
        
        # 2. Установка Composer
        print("\n2. УСТАНОВКА COMPOSER:")
        success, output = ssh_exec(ssh, "composer --version 2>&1")
        
        if not success or "Composer" not in output:
            print("  Установка Composer...")
            ssh_exec(ssh, "curl -sS https://getcomposer.org/installer | php", "Загрузка Composer")
            ssh_exec(ssh, "mv composer.phar /usr/local/bin/composer && chmod +x /usr/local/bin/composer", "Установка Composer")
        else:
            print(f"  [OK] Composer уже установлен")
        
        success, output = ssh_exec(ssh, "composer --version")
        print(f"  {output.split(chr(10))[0]}")
        
        # 3. Копирование файлов Laravel backend
        print("\n3. КОПИРОВАНИЕ ФАЙЛОВ LARAVEL:")
        ssh_exec(ssh, f"mkdir -p {BACKEND_DIR}", "Создание директории")
        
        # Используем git для получения файлов
        ssh_exec(ssh, f"cd /root/shannon && git pull", "Обновление репозитория")
        
        # 4. Установка зависимостей Laravel
        print("\n4. УСТАНОВКА ЗАВИСИМОСТЕЙ LARAVEL:")
        success, output = ssh_exec(ssh, f"cd {BACKEND_DIR} && composer install --no-dev --optimize-autoloader 2>&1", "Установка Composer зависимостей")
        if not success:
            print(f"  [WARNING] Возможны ошибки: {output[-500:]}")
        
        # 5. Настройка .env
        print("\n5. НАСТРОЙКА ОКРУЖЕНИЯ:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && [ ! -f .env ] && cp .env.example .env || echo 'exists'", "Создание .env")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan key:generate --force 2>&1", "Генерация APP_KEY")
        
        # Настройка базы данных
        ssh_exec(ssh, f"cd {BACKEND_DIR} && sed -i 's/DB_CONNECTION=.*/DB_CONNECTION=sqlite/' .env 2>&1 || echo 'config'", "Настройка БД")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && sed -i 's|DB_DATABASE=.*|DB_DATABASE={BACKEND_DIR}/database/database.sqlite|' .env 2>&1 || echo 'config'", "Настройка пути")
        
        # 6. Создание базы данных и миграции
        print("\n6. НАСТРОЙКА БАЗЫ ДАННЫХ:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && mkdir -p database && touch database/database.sqlite", "Создание БД")
        success, output = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan migrate --force 2>&1", "Запуск миграций")
        if not success:
            print(f"  [WARNING] Возможны ошибки миграций: {output[-500:]}")
        
        # 7. Настройка прав доступа
        print("\n7. НАСТРОЙКА ПРАВ ДОСТУПА:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && mkdir -p storage/framework/cache storage/framework/sessions storage/framework/views storage/logs bootstrap/cache", "Создание директорий")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && chmod -R 775 storage bootstrap/cache", "Настройка прав")
        
        # 8. Оптимизация
        print("\n8. ОПТИМИЗАЦИЯ:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan config:cache 2>&1", "Кэширование конфигурации")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan route:cache 2>&1", "Кэширование маршрутов")
        
        # 9. Создание systemd service
        print("\n9. СОЗДАНИЕ SYSTEMD SERVICE:")
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
        success, output = ssh_exec(ssh, "systemctl status shannon-laravel.service --no-pager -l | head -15")
        if "active (running)" in output.lower():
            print("  [OK] Сервис запущен и работает")
        else:
            print(f"  [WARNING] Статус сервиса: {output[:200]}")
        
        # 10. Настройка Frontend
        print("\n10. НАСТРОЙКА FRONTEND:")
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && cat > .env << 'EOFFRONTEND'\nVITE_API_URL=https://{SSH_HOST}/api\nEOFFRONTEND", "Создание .env")
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && npm install 2>&1 | tail -5", "Установка зависимостей")
        success, output = ssh_exec(ssh, f"cd {FRONTEND_DIR} && npm run build 2>&1 | tail -10", "Сборка frontend")
        
        # 11. Настройка Nginx
        print("\n11. НАСТРОЙКА NGINX:")
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
        ssh_exec(ssh, "rm -f /etc/nginx/sites-enabled/default", "Удаление default")
        
        success, output = ssh_exec(ssh, "nginx -t 2>&1")
        if "successful" in output.lower():
            ssh_exec(ssh, "systemctl reload nginx", "Перезагрузка Nginx")
            print("  [OK] Nginx настроен")
        else:
            print(f"  [ERROR] Ошибка Nginx: {output}")
        
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
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

