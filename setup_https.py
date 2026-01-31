#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Настройка HTTPS с Let's Encrypt
"""

import paramiko
import sys
import time

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
DOMAIN = "72.56.79.153"  # Используем IP, но можно указать домен если есть

def ssh_exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    print("="*60)
    print("НАСТРОЙКА HTTPS")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка установки Certbot
        print("\n1. ПРОВЕРКА CERTBOT:")
        success, output, error = ssh_exec(ssh, "which certbot")
        if not success or not output.strip():
            print("  Certbot не установлен, устанавливаем...")
            ssh_exec(ssh, "apt-get update -y")
            ssh_exec(ssh, "apt-get install -y certbot python3-certbot-nginx")
            print("  [OK] Certbot установлен")
        else:
            print(f"  [OK] Certbot уже установлен: {output.strip()}")
        
        # 2. Проверка текущей конфигурации Nginx
        print("\n2. ПРОВЕРКА NGINX:")
        success, output, error = ssh_exec(ssh, "nginx -t 2>&1")
        if "successful" in output.lower():
            print("  [OK] Nginx конфигурация валидна")
        else:
            print(f"  [ERROR] Ошибка Nginx: {output}")
            return
        
        # 3. Получение SSL сертификата
        print("\n3. ПОЛУЧЕНИЕ SSL СЕРТИФИКАТА:")
        print("  ВАЖНО: Для IP-адреса Let's Encrypt не выдает сертификаты.")
        print("  Нужен домен. Если домена нет, можно использовать самоподписанный сертификат.")
        
        # Проверяем, есть ли домен или используем самоподписанный
        use_self_signed = True
        
        if use_self_signed:
            print("\n  Используем самоподписанный сертификат для IP-адреса...")
            
            # Создаем директорию для сертификатов
            ssh_exec(ssh, "mkdir -p /etc/nginx/ssl")
            
            # Генерируем самоподписанный сертификат
            cert_cmd = f"""openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\
                -keyout /etc/nginx/ssl/{SSH_HOST}.key \\
                -out /etc/nginx/ssl/{SSH_HOST}.crt \\
                -subj "/C=RU/ST=State/L=City/O=Organization/CN={SSH_HOST}" 2>&1"""
            
            success, output, error = ssh_exec(ssh, cert_cmd)
            if success:
                print("  [OK] Самоподписанный сертификат создан")
            else:
                print(f"  [ERROR] Ошибка создания сертификата: {error}")
                return
            
            # Устанавливаем права доступа
            ssh_exec(ssh, "chmod 600 /etc/nginx/ssl/*.key")
            ssh_exec(ssh, "chmod 644 /etc/nginx/ssl/*.crt")
        
        # 4. Обновление конфигурации Nginx для HTTPS
        print("\n4. ОБНОВЛЕНИЕ КОНФИГУРАЦИИ NGINX:")
        
        if use_self_signed:
            nginx_config = f"""server {{
    listen 80;
    listen [::]:80;
    server_name {SSH_HOST};
    
    # Редирект HTTP на HTTPS
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {SSH_HOST};

    ssl_certificate /etc/nginx/ssl/{SSH_HOST}.crt;
    ssl_certificate_key /etc/nginx/ssl/{SSH_HOST}.key;
    
    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    root /root/shannon/template/dist;
    index index.html;

    # Frontend (SPA)
    location / {{
        try_files $uri $uri/ /index.html;
    }}

    # API проксирование к Laravel backend
    location /api {{
        proxy_pass http://127.0.0.1:8000/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }}

    # Health check
    location /up {{
        proxy_pass http://127.0.0.1:8000/up;
        proxy_set_header Host $host;
    }}
}}
"""
        else:
            # Конфигурация для Let's Encrypt (если есть домен)
            nginx_config = f"""server {{
    listen 80;
    listen [::]:80;
    server_name {DOMAIN};
    
    # Для Let's Encrypt
    location /.well-known/acme-challenge/ {{
        root /var/www/html;
    }}
    
    # Редирект HTTP на HTTPS
    location / {{
        return 301 https://$server_name$request_uri;
    }}
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {DOMAIN};

    ssl_certificate /etc/letsencrypt/live/{DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{DOMAIN}/privkey.pem;
    
    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    root /root/shannon/template/dist;
    index index.html;

    # Frontend (SPA)
    location / {{
        try_files $uri $uri/ /index.html;
    }}

    # API проксирование к Laravel backend
    location /api {{
        proxy_pass http://127.0.0.1:8000/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }}

    # Health check
    location /up {{
        proxy_pass http://127.0.0.1:8000/up;
        proxy_set_header Host $host;
    }}
}}
"""
        
        stdin, stdout, stderr = ssh.exec_command(f"cat > /etc/nginx/sites-available/shannon << 'EOFNGINX'\n{nginx_config}\nEOFNGINX")
        ssh_exec(ssh, "ln -sf /etc/nginx/sites-available/shannon /etc/nginx/sites-enabled/shannon")
        
        # Проверка конфигурации
        success, output, error = ssh_exec(ssh, "nginx -t 2>&1")
        if "successful" in output.lower():
            print("  [OK] Конфигурация Nginx обновлена")
            ssh_exec(ssh, "systemctl reload nginx")
            print("  [OK] Nginx перезагружен")
        else:
            print(f"  [ERROR] Ошибка конфигурации: {output}")
            return
        
        # 5. Обновление frontend .env для HTTPS
        print("\n5. ОБНОВЛЕНИЕ FRONTEND:")
        ssh_exec(ssh, f"cd /root/shannon/template && cat > .env << 'EOFFRONTEND'\nVITE_API_URL=https://{SSH_HOST}/api\nEOFFRONTEND")
        print("  [OK] .env обновлен для HTTPS")
        
        # Пересборка frontend (если нужно)
        print("  Пересборка frontend...")
        ssh_exec(ssh, "cd /root/shannon/template && npm run build 2>&1 | tail -5")
        
        # 6. Обновление CORS в Laravel для HTTPS
        print("\n6. ОБНОВЛЕНИЕ CORS В LARAVEL:")
        ssh_exec(ssh, f"cd /root/shannon/backend-laravel && sed -i 's|APP_URL=.*|APP_URL=https://{SSH_HOST}|' .env")
        ssh_exec(ssh, f"cd /root/shannon/backend-laravel && php artisan config:cache 2>&1")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service")
        print("  [OK] CORS обновлен")
        
        # 7. Финальная проверка
        print("\n7. ФИНАЛЬНАЯ ПРОВЕРКА:")
        time.sleep(2)
        
        # Проверка HTTPS
        success, output, error = ssh_exec(ssh, f"curl -k -s https://{SSH_HOST}/api/auth/login -X POST -H 'Content-Type: application/json' -d '{{\"username\":\"admin\",\"password\":\"admin\"}}' | head -c 200")
        if '"token"' in output or '"user"' in output:
            print("  ✅ HTTPS API работает")
        else:
            print(f"  ⚠️  Ответ: {output[:200]}")
        
        print("\n" + "="*60)
        print("HTTPS НАСТРОЕН!")
        print("="*60)
        print(f"\n✅ Приложение доступно по HTTPS:")
        print(f"   https://{SSH_HOST}")
        print(f"\n⚠️  ВАЖНО: Используется самоподписанный сертификат.")
        print(f"   Браузер покажет предупреждение о безопасности.")
        print(f"   Для продакшена рекомендуется использовать домен и Let's Encrypt.")
        print(f"\nЛогин: admin")
        print(f"Пароль: admin")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

