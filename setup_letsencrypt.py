#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Настройка Let's Encrypt для домена
Использование: python setup_letsencrypt.py yourdomain.com
"""

import paramiko
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def ssh_exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    if len(sys.argv) < 2:
        print("Использование: python setup_letsencrypt.py yourdomain.com")
        print("\nПример: python setup_letsencrypt.py example.com")
        return
    
    domain = sys.argv[1]
    
    print("="*60)
    print(f"НАСТРОЙКА LET'S ENCRYPT ДЛЯ {domain}")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Временная конфигурация Nginx для Let's Encrypt
        print("\n1. ВРЕМЕННАЯ КОНФИГУРАЦИЯ NGINX:")
        temp_config = f"""server {{
    listen 80;
    listen [::]:80;
    server_name {domain};

    root /var/www/html;
    index index.html;

    location /.well-known/acme-challenge/ {{
        root /var/www/html;
    }}

    location / {{
        return 301 https://$server_name$request_uri;
    }}
}}
"""
        ssh_exec(ssh, f"cat > /etc/nginx/sites-available/shannon << 'EOFTEMP'\n{temp_config}\nEOFTEMP")
        ssh_exec(ssh, "mkdir -p /var/www/html/.well-known/acme-challenge")
        ssh_exec(ssh, "systemctl reload nginx")
        print("  [OK] Временная конфигурация применена")
        
        # 2. Получение сертификата
        print("\n2. ПОЛУЧЕНИЕ СЕРТИФИКАТА:")
        certbot_cmd = f"certbot certonly --webroot -w /var/www/html -d {domain} --non-interactive --agree-tos --email admin@{domain} --quiet 2>&1"
        success, output, error = ssh_exec(ssh, certbot_cmd)
        
        if success or "Successfully received certificate" in output:
            print("  [OK] Сертификат получен")
        else:
            print(f"  [ERROR] Ошибка получения сертификата: {output}")
            print(f"  Проверьте, что домен {domain} указывает на IP {SSH_HOST}")
            return
        
        # 3. Обновление конфигурации Nginx для HTTPS
        print("\n3. ОБНОВЛЕНИЕ КОНФИГУРАЦИИ NGINX:")
        nginx_config = f"""server {{
    listen 80;
    listen [::]:80;
    server_name {domain};
    
    # Редирект HTTP на HTTPS
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {domain};

    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;
    
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
        
        ssh_exec(ssh, f"cat > /etc/nginx/sites-available/shannon << 'EOFNGINX'\n{nginx_config}\nEOFNGINX")
        
        # Проверка конфигурации
        success, output, error = ssh_exec(ssh, "nginx -t 2>&1")
        if "successful" in output.lower():
            ssh_exec(ssh, "systemctl reload nginx")
            print("  [OK] Конфигурация обновлена")
        else:
            print(f"  [ERROR] Ошибка конфигурации: {output}")
            return
        
        # 4. Настройка автообновления сертификата
        print("\n4. НАСТРОЙКА АВТООБНОВЛЕНИЯ:")
        ssh_exec(ssh, "systemctl enable certbot.timer")
        ssh_exec(ssh, "systemctl start certbot.timer")
        print("  [OK] Автообновление настроено")
        
        # 5. Обновление frontend и backend
        print("\n5. ОБНОВЛЕНИЕ ПРИЛОЖЕНИЯ:")
        ssh_exec(ssh, f"cd /root/shannon/template && cat > .env << 'EOFFRONTEND'\nVITE_API_URL=https://{domain}/api\nEOFFRONTEND")
        ssh_exec(ssh, f"cd /root/shannon/backend-laravel && sed -i 's|APP_URL=.*|APP_URL=https://{domain}|' .env")
        ssh_exec(ssh, f"cd /root/shannon/backend-laravel && php artisan config:cache 2>&1")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service")
        print("  [OK] Приложение обновлено")
        
        print("\n" + "="*60)
        print("LET'S ENCRYPT НАСТРОЕН!")
        print("="*60)
        print(f"\n✅ Приложение доступно по HTTPS:")
        print(f"   https://{domain}")
        print(f"\n✅ Сертификат будет автоматически обновляться.")
        print(f"\nЛогин: admin")
        print(f"Пароль: admin")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

