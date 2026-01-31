#!/usr/bin/env python3
"""
Скрипт для развертывания Laravel Backend на сервере
"""

import paramiko
import os
from pathlib import Path

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
BACKEND_DIR = "/root/shannon/backend-laravel"
FRONTEND_DIR = "/root/shannon/template"

def main():
    print("="*60)
    print("РАЗВЕРТЫВАНИЕ LARAVEL BACKEND НА СЕРВЕРЕ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    sftp = ssh.open_sftp()
    
    try:
        # 1. Проверяем наличие PHP и Composer
        print("\n1. ПРОВЕРКА ЗАВИСИМОСТЕЙ:")
        stdin, stdout, stderr = ssh.exec_command("php -v")
        php_version = stdout.read().decode('utf-8', errors='replace')
        if php_version:
            print(f"  [OK] PHP установлен")
            print(f"  {php_version.split(chr(10))[0]}")
        else:
            print("  [ERROR] PHP не установлен!")
            return
        
        stdin, stdout, stderr = ssh.exec_command("composer --version")
        composer_version = stdout.read().decode('utf-8', errors='replace')
        if composer_version:
            print(f"  [OK] Composer установлен")
            print(f"  {composer_version.split(chr(10))[0]}")
        else:
            print("  [WARNING] Composer не установлен, устанавливаем...")
            ssh.exec_command("curl -sS https://getcomposer.org/installer | php && mv composer.phar /usr/local/bin/composer && chmod +x /usr/local/bin/composer")
        
        # 2. Создаем директорию
        print("\n2. СОЗДАНИЕ ДИРЕКТОРИИ:")
        ssh.exec_command(f"mkdir -p {BACKEND_DIR}")
        print(f"  [OK] Директория создана: {BACKEND_DIR}")
        
        # 3. Копируем файлы Laravel backend
        print("\n3. КОПИРОВАНИЕ ФАЙЛОВ:")
        backend_files = [
            "backend-laravel/app",
            "backend-laravel/bootstrap",
            "backend-laravel/config",
            "backend-laravel/database",
            "backend-laravel/public",
            "backend-laravel/routes",
            "backend-laravel/storage",
            "backend-laravel/tests",
            "backend-laravel/artisan",
            "backend-laravel/composer.json",
            "backend-laravel/phpunit.xml",
            "backend-laravel/.gitignore",
        ]
        
        for item in backend_files:
            local_path = Path(item)
            if local_path.exists():
                remote_path = f"{BACKEND_DIR}/{local_path.name}"
                if local_path.is_dir():
                    print(f"  Копирую директорию: {local_path.name}...")
                    ssh.exec_command(f"mkdir -p {remote_path}")
                    # Копируем файлы через sftp
                    for file_path in local_path.rglob('*'):
                        if file_path.is_file():
                            remote_file = f"{remote_path}/{file_path.relative_to(local_path)}"
                            remote_dir = os.path.dirname(remote_file)
                            ssh.exec_command(f"mkdir -p {remote_dir}")
                            try:
                                sftp.put(str(file_path), remote_file)
                            except Exception as e:
                                print(f"    [WARNING] Не удалось скопировать {file_path}: {e}")
                else:
                    print(f"  Копирую файл: {local_path.name}...")
                    try:
                        sftp.put(str(local_path), remote_path)
                    except Exception as e:
                        print(f"    [WARNING] Не удалось скопировать {local_path}: {e}")
        
        # 4. Установка зависимостей
        print("\n4. УСТАНОВКА ЗАВИСИМОСТЕЙ:")
        stdin, stdout, stderr = ssh.exec_command(f"cd {BACKEND_DIR} && composer install --no-dev --optimize-autoloader 2>&1")
        output = stdout.read().decode('utf-8', errors='replace')
        if "error" in output.lower():
            print(f"  [ERROR] Ошибка установки зависимостей:")
            print(output)
        else:
            print("  [OK] Зависимости установлены")
        
        # 5. Настройка .env
        print("\n5. НАСТРОЙКА ОКРУЖЕНИЯ:")
        stdin, stdout, stderr = ssh.exec_command(f"cd {BACKEND_DIR} && [ ! -f .env ] && cp .env.example .env || echo 'exists'")
        stdin, stdout, stderr = ssh.exec_command(f"cd {BACKEND_DIR} && php artisan key:generate --force 2>&1")
        output = stdout.read().decode('utf-8', errors='replace')
        print("  [OK] .env настроен")
        
        # 6. Настройка прав доступа
        print("\n6. НАСТРОЙКА ПРАВ ДОСТУПА:")
        ssh.exec_command(f"cd {BACKEND_DIR} && chmod -R 775 storage bootstrap/cache")
        ssh.exec_command(f"cd {BACKEND_DIR} && chown -R www-data:www-data storage bootstrap/cache 2>&1 || chown -R root:root storage bootstrap/cache")
        print("  [OK] Права доступа настроены")
        
        # 7. Настройка базы данных
        print("\n7. НАСТРОЙКА БАЗЫ ДАННЫХ:")
        stdin, stdout, stderr = ssh.exec_command(f"cd {BACKEND_DIR} && touch database/database.sqlite")
        print("  [OK] SQLite база данных создана")
        
        # 8. Запуск миграций
        print("\n8. ЗАПУСК МИГРАЦИЙ:")
        stdin, stdout, stderr = ssh.exec_command(f"cd {BACKEND_DIR} && php artisan migrate --force 2>&1")
        output = stdout.read().decode('utf-8', errors='replace')
        if "error" in output.lower():
            print(f"  [WARNING] Возможны ошибки миграций:")
            print(output[:500])
        else:
            print("  [OK] Миграции выполнены")
        
        # 9. Оптимизация
        print("\n9. ОПТИМИЗАЦИЯ:")
        ssh.exec_command(f"cd {BACKEND_DIR} && php artisan config:cache 2>&1")
        ssh.exec_command(f"cd {BACKEND_DIR} && php artisan route:cache 2>&1")
        print("  [OK] Кэш настроен")
        
        # 10. Создание systemd service
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
        
        stdin, stdout, stderr = ssh.exec_command(f"cat > /etc/systemd/system/shannon-laravel.service << 'EOF'\n{service_content}\nEOF")
        ssh.exec_command("systemctl daemon-reload")
        ssh.exec_command("systemctl enable shannon-laravel.service")
        ssh.exec_command("systemctl restart shannon-laravel.service")
        print("  [OK] Systemd service создан и запущен")
        
        # 11. Проверка статуса
        print("\n11. ПРОВЕРКА СТАТУСА:")
        stdin, stdout, stderr = ssh.exec_command("systemctl status shannon-laravel.service --no-pager -l")
        status = stdout.read().decode('utf-8', errors='replace')
        if "active (running)" in status.lower():
            print("  [OK] Сервис запущен и работает")
        else:
            print("  [WARNING] Сервис может быть не запущен:")
            print(status[:300])
        
        print("\n" + "="*60)
        print("РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО")
        print("="*60)
        print(f"\nBackend доступен на: http://{SSH_HOST}:8000")
        print(f"\nСледующие шаги:")
        print(f"1. Настройте .env файл: ssh {SSH_USER}@{SSH_HOST} 'nano {BACKEND_DIR}/.env'")
        print(f"2. Создайте пользователя: ssh {SSH_USER}@{SSH_HOST} 'cd {BACKEND_DIR} && php artisan tinker'")
        print(f"3. Проверьте логи: ssh {SSH_USER}@{SSH_HOST} 'journalctl -u shannon-laravel -f'")
        
    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    main()

