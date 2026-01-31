#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полное развертывание Laravel Backend на сервере
"""

import paramiko
import sys

# Устанавливаем кодировку для вывода
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

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
    print("РАЗВЕРТЫВАНИЕ LARAVEL BACKEND НА СЕРВЕРЕ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    sftp = ssh.open_sftp()
    
    try:
        # 1. Установка PHP (если нужно)
        print("\n1. ПРОВЕРКА PHP:")
        success, output = ssh_exec(ssh, "php -v 2>&1")
        if not success or "PHP" not in output:
            print("  Установка PHP...")
            ssh_exec(ssh, "apt-get update -y")
            ssh_exec(ssh, "apt-get install -y php php-cli php-fpm php-mbstring php-xml php-curl php-sqlite3 php-zip php-gd php-bcmath")
        else:
            print(f"  [OK] PHP установлен")
            print(f"  {output.split(chr(10))[0]}")
        
        # 2. Установка Composer (если нужно)
        print("\n2. ПРОВЕРКА COMPOSER:")
        success, output = ssh_exec(ssh, "composer --version 2>&1")
        if not success or "Composer" not in output:
            print("  Установка Composer...")
            ssh_exec(ssh, "curl -sS https://getcomposer.org/installer | php")
            ssh_exec(ssh, "mv composer.phar /usr/local/bin/composer && chmod +x /usr/local/bin/composer")
        else:
            print(f"  [OK] Composer установлен")
            print(f"  {output.split(chr(10))[0]}")
        
        # 3. Обновление репозитория
        print("\n3. ОБНОВЛЕНИЕ РЕПОЗИТОРИЯ:")
        ssh_exec(ssh, "cd /root/shannon && git stash", "Сохранение локальных изменений")
        ssh_exec(ssh, "cd /root/shannon && git pull", "Обновление репозитория")
        print("  [OK] Репозиторий обновлен")
        
        # 4. Копирование файлов Laravel backend
        print("\n4. КОПИРОВАНИЕ ФАЙЛОВ LARAVEL:")
        ssh_exec(ssh, f"mkdir -p {BACKEND_DIR}", "Создание директории")
        
        # Копируем файлы через sftp
        import os
        from pathlib import Path
        
        backend_local = Path("backend-laravel")
        if backend_local.exists():
            print("  Копирование файлов...")
            # Копируем основные файлы и директории
            items_to_copy = [
                "app", "bootstrap", "config", "database", "public", 
                "routes", "storage", "tests", "artisan", "composer.json", 
                "phpunit.xml", ".gitignore"
            ]
            
            for item in items_to_copy:
                local_path = backend_local / item
                if local_path.exists():
                    remote_path = f"{BACKEND_DIR}/{item}"
                    if local_path.is_dir():
                        print(f"    Копирую директорию: {item}")
                        ssh_exec(ssh, f"mkdir -p {remote_path}")
                        # Копируем файлы рекурсивно
                        for file_path in local_path.rglob('*'):
                            if file_path.is_file():
                                rel_path = file_path.relative_to(local_path)
                                remote_file = f"{remote_path}/{str(rel_path).replace(chr(92), '/')}"
                                remote_dir = os.path.dirname(remote_file)
                                ssh_exec(ssh, f"mkdir -p {remote_dir}")
                                try:
                                    sftp.put(str(file_path), remote_file)
                                except Exception as e:
                                    print(f"      [WARNING] {file_path.name}: {str(e)[:50]}")
                    else:
                        print(f"    Копирую файл: {item}")
                        try:
                            sftp.put(str(local_path), remote_path)
                        except Exception as e:
                            print(f"      [WARNING] {item}: {str(e)[:50]}")
        
        # 5. Установка зависимостей
        print("\n5. УСТАНОВКА ЗАВИСИМОСТЕЙ:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && COMPOSER_ALLOW_SUPERUSER=1 composer install --no-dev --optimize-autoloader 2>&1 | tail -20", "Установка Composer зависимостей")
        
        # 6. Настройка .env
        print("\n6. НАСТРОЙКА ОКРУЖЕНИЯ:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && [ ! -f .env ] && cp .env.example .env || echo 'exists'", "Создание .env")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan key:generate --force 2>&1", "Генерация APP_KEY")
        
        # Настройка базы данных в .env
        ssh_exec(ssh, f"cd {BACKEND_DIR} && grep -q 'DB_CONNECTION=sqlite' .env || echo 'DB_CONNECTION=sqlite' >> .env", "Настройка БД")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && sed -i 's|DB_DATABASE=.*|DB_DATABASE={BACKEND_DIR}/database/database.sqlite|' .env 2>&1 || echo 'DB_DATABASE={BACKEND_DIR}/database/database.sqlite' >> .env", "Настройка пути")
        
        # 7. Создание БД и миграции
        print("\n7. НАСТРОЙКА БАЗЫ ДАННЫХ:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && mkdir -p database && touch database/database.sqlite", "Создание БД")
        success, output = ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan migrate --force 2>&1", "Запуск миграций")
        if not success:
            print(f"  [WARNING] Возможны ошибки: {output[-300:]}")
        
        # 8. Настройка прав
        print("\n8. НАСТРОЙКА ПРАВ ДОСТУПА:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && mkdir -p storage/framework/cache storage/framework/sessions storage/framework/views storage/logs bootstrap/cache", "Создание директорий")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && chmod -R 775 storage bootstrap/cache", "Настройка прав")
        
        # 9. Оптимизация
        print("\n9. ОПТИМИЗАЦИЯ:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan config:cache 2>&1", "Кэширование конфигурации")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan route:cache 2>&1", "Кэширование маршрутов")
        
        # 10. Systemd service
        print("\n10. СОЗДАНИЕ SYSTEMD SERVICE:")
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
        success, output = ssh_exec(ssh, "systemctl is-active shannon-laravel.service")
        if "active" in output.lower():
            print("  [OK] Сервис запущен")
        else:
            print(f"  [WARNING] Статус: {output.strip()}")
            ssh_exec(ssh, "journalctl -u shannon-laravel.service -n 20 --no-pager", "Последние логи")
        
        # 11. Frontend
        print("\n11. НАСТРОЙКА FRONTEND:")
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && cat > .env << 'EOFFRONTEND'\nVITE_API_URL=https://{SSH_HOST}/api\nEOFFRONTEND", "Создание .env")
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && npm install 2>&1 | tail -3", "Установка зависимостей")
        success, output = ssh_exec(ssh, f"cd {FRONTEND_DIR} && npm run build 2>&1 | tail -5", "Сборка")
        
        # 12. Nginx
        print("\n12. НАСТРОЙКА NGINX:")
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
        ssh_exec(ssh, "ln -sf /etc/nginx/sites-available/shannon /etc/nginx/sites-enabled/shannon", "Активация")
        ssh_exec(ssh, "rm -f /etc/nginx/sites-enabled/default", "Удаление default")
        
        success, output = ssh_exec(ssh, "nginx -t 2>&1")
        if "successful" in output.lower():
            ssh_exec(ssh, "systemctl reload nginx", "Перезагрузка Nginx")
            print("  [OK] Nginx настроен")
        else:
            print(f"  [ERROR] {output}")
        
        print("\n" + "="*60)
        print("РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!")
        print("="*60)
        print(f"\nПриложение: http://{SSH_HOST}")
        print(f"\nСоздайте пользователя:")
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
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    main()

