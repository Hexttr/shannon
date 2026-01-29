#!/usr/bin/env python3
"""
Глубокая проверка всех аспектов приложения
"""

import paramiko
import sys
import socket

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

def check_port(host, port):
    """Проверяет доступность порта"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print("="*60)
    print("ГЛУБОКАЯ ПРОВЕРКА ПРИЛОЖЕНИЯ")
    print("="*60)
    
    # Проверка доступности портов извне
    print("\n0. Проверяю доступность портов извне...")
    http_available = check_port(SSH_HOST, 80)
    https_available = check_port(SSH_HOST, 443)
    print(f"HTTP (80): {'[OK] Доступен' if http_available else '[FAIL] Недоступен'}")
    print(f"HTTPS (443): {'[OK] Доступен' if https_available else '[FAIL] Недоступен'}")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        print("Подключение установлено!")
    except Exception as e:
        print(f"Ошибка подключения: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 1. Проверяем все активные конфигурации nginx
        print("\n1. Проверяю все конфигурации nginx...")
        execute_ssh_command(
            ssh,
            "ls -la /etc/nginx/sites-enabled/",
            "Активные конфигурации nginx"
        )
        
        execute_ssh_command(
            ssh,
            "ls -la /etc/nginx/sites-available/",
            "Доступные конфигурации nginx"
        )
        
        # 2. Проверяем все server блоки в конфигурациях
        print("\n2. Проверяю все server блоки...")
        execute_ssh_command(
            ssh,
            "grep -r 'server_name.*72.56.79.153' /etc/nginx/ 2>/dev/null | head -20",
            "Все server_name для 72.56.79.153"
        )
        
        execute_ssh_command(
            ssh,
            "grep -r 'listen.*443' /etc/nginx/sites-enabled/ 2>/dev/null",
            "HTTPS конфигурации"
        )
        
        # 3. Проверяем основную конфигурацию nginx
        print("\n3. Проверяю основную конфигурацию nginx...")
        execute_ssh_command(
            ssh,
            "cat /etc/nginx/nginx.conf | grep -A 5 'include' | head -20",
            "Основная конфигурация nginx"
        )
        
        # 4. Проверяем конфигурацию shannon
        print("\n4. Проверяю конфигурацию shannon...")
        execute_ssh_command(
            ssh,
            "cat /etc/nginx/sites-available/shannon",
            "Конфигурация shannon"
        )
        
        # 5. Проверяем, какие порты слушает nginx
        print("\n5. Проверяю порты nginx...")
        execute_ssh_command(
            ssh,
            "ss -tlnp | grep nginx || netstat -tlnp | grep nginx",
            "Порты nginx"
        )
        
        # 6. Проверяем firewall правила
        print("\n6. Проверяю firewall правила...")
        execute_ssh_command(
            ssh,
            "ufw status 2>/dev/null || iptables -L -n | grep -E '80|443' | head -10 || echo 'Firewall не настроен или недоступен'",
            "Firewall правила"
        )
        
        # 7. Тестируем HTTP запрос напрямую
        print("\n7. Тестирую HTTP запрос напрямую...")
        execute_ssh_command(
            ssh,
            "curl -v http://localhost/ 2>&1 | head -30",
            "HTTP запрос к localhost"
        )
        
        execute_ssh_command(
            ssh,
            "curl -v http://72.56.79.153/ 2>&1 | head -30",
            "HTTP запрос по IP"
        )
        
        # 8. Тестируем HTTPS запрос
        print("\n8. Тестирую HTTPS запрос...")
        execute_ssh_command(
            ssh,
            "curl -v -k https://localhost/ 2>&1 | head -30",
            "HTTPS запрос к localhost"
        )
        
        execute_ssh_command(
            ssh,
            "curl -v -k https://72.56.79.153/ 2>&1 | head -30",
            "HTTPS запрос по IP"
        )
        
        # 9. Проверяем содержимое index.html
        print("\n9. Проверяю содержимое index.html...")
        execute_ssh_command(
            ssh,
            "cat /var/www/shannon/index.html",
            "Содержимое index.html"
        )
        
        # 10. Проверяем права доступа к файлам
        print("\n10. Проверяю права доступа...")
        execute_ssh_command(
            ssh,
            "ls -la /var/www/shannon/",
            "Права доступа к файлам"
        )
        
        execute_ssh_command(
            ssh,
            "stat /var/www/shannon/index.html",
            "Детальная информация о index.html"
        )
        
        # 11. Проверяем логи nginx в реальном времени
        print("\n11. Проверяю последние логи nginx...")
        execute_ssh_command(
            ssh,
            "tail -50 /var/log/nginx/access.log | tail -20",
            "Последние запросы в access.log"
        )
        
        execute_ssh_command(
            ssh,
            "tail -50 /var/log/nginx/error.log | grep -v 'phpunit' | tail -20",
            "Последние ошибки в error.log"
        )
        
        # 12. Проверяем, есть ли другие сервисы на портах 80/443
        print("\n12. Проверяю процессы на портах 80/443...")
        execute_ssh_command(
            ssh,
            "lsof -i :80 2>/dev/null || fuser 80/tcp 2>/dev/null || ss -tlnp | grep ':80'",
            "Процессы на порту 80"
        )
        
        execute_ssh_command(
            ssh,
            "lsof -i :443 2>/dev/null || fuser 443/tcp 2>/dev/null || ss -tlnp | grep ':443'",
            "Процессы на порту 443"
        )
        
        # 13. Проверяем, есть ли редиректы
        print("\n13. Проверяю редиректы...")
        execute_ssh_command(
            ssh,
            "curl -I http://72.56.79.153/ 2>&1 | head -15",
            "HTTP заголовки с редиректами"
        )
        
        execute_ssh_command(
            ssh,
            "curl -I https://72.56.79.153/ 2>&1 | head -15",
            "HTTPS заголовки с редиректами"
        )
        
        # 14. Проверяем, что возвращает сервер при запросе
        print("\n14. Проверяю ответ сервера...")
        execute_ssh_command(
            ssh,
            "curl -s http://72.56.79.153/ | head -20",
            "Содержимое ответа HTTP"
        )
        
        execute_ssh_command(
            ssh,
            "curl -s -k https://72.56.79.153/ 2>&1 | head -20",
            "Содержимое ответа HTTPS"
        )
        
        # 15. Проверяем конфигурацию default nginx
        print("\n15. Проверяю default конфигурацию nginx...")
        execute_ssh_command(
            ssh,
            "cat /etc/nginx/sites-available/default 2>/dev/null | head -50 || echo 'default конфигурация не найдена'",
            "Default конфигурация"
        )
        
        # 16. Исправляем проблемы
        print("\n16. Анализирую и исправляю проблемы...")
        
        # Проверяем, есть ли HTTPS конфигурация, которая может конфликтовать
        stdin, stdout, stderr = ssh.exec_command("grep -r 'listen.*443' /etc/nginx/sites-enabled/ 2>/dev/null | wc -l")
        https_configs = int(stdout.read().decode('utf-8', errors='replace').strip() or 0)
        
        if https_configs > 0:
            print(f"Найдено {https_configs} HTTPS конфигураций. Проверяю их...")
            execute_ssh_command(
                ssh,
                "grep -r -A 10 'listen.*443' /etc/nginx/sites-enabled/ 2>/dev/null",
                "HTTPS конфигурации"
            )
        
        # Создаем правильную конфигурацию для HTTP и HTTPS
        print("\n17. Создаю правильную конфигурацию...")
        
        web_dir = "/var/www/shannon"
        
        # HTTP конфигурация
        nginx_config_http = f"""server {{
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
        stdin, stdout, stderr = ssh.exec_command(f"cat > {config_file} << 'NGINX_EOF'\n{nginx_config_http}\nNGINX_EOF\n")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Конфигурация обновлена!")
        
        # Активируем конфигурацию
        execute_ssh_command(
            ssh,
            "ln -sf /etc/nginx/sites-available/shannon /etc/nginx/sites-enabled/shannon",
            "Активация конфигурации"
        )
        
        # Отключаем default если он активен и конфликтует
        execute_ssh_command(
            ssh,
            "rm -f /etc/nginx/sites-enabled/default",
            "Отключение default конфигурации"
        )
        
        # 18. Проверяем и перезапускаем nginx
        print("\n18. Проверяю и перезапускаю nginx...")
        execute_ssh_command(ssh, "nginx -t", "Проверка конфигурации")
        execute_ssh_command(ssh, "systemctl reload nginx", "Перезагрузка nginx")
        execute_ssh_command(ssh, "systemctl status nginx --no-pager | head -10", "Статус nginx")
        
        # 19. Финальная проверка
        print("\n19. Финальная проверка...")
        execute_ssh_command(
            ssh,
            "curl -v http://72.56.79.153/ 2>&1 | head -40",
            "Финальная проверка HTTP"
        )
        
        execute_ssh_command(
            ssh,
            "curl -v -k https://72.56.79.153/ 2>&1 | head -40",
            "Финальная проверка HTTPS"
        )
        
        print("\n" + "="*60)
        print("ГЛУБОКАЯ ПРОВЕРКА ЗАВЕРШЕНА")
        print("="*60)
        print(f"\nHTTP: http://{SSH_HOST}/")
        print(f"HTTPS: https://{SSH_HOST}/")
        print(f"Backend API: http://{SSH_HOST}/api/")
        print("\nПроверьте работу в браузере!")
        
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

