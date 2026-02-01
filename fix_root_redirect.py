#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление редиректа с корневого пути
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
    print("="*70)
    print("ИСПРАВЛЕНИЕ РЕДИРЕКТА С КОРНЕВОГО ПУТИ")
    print("="*70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Обновляем конфигурацию Nginx с правильным редиректом
        nginx_config = """server {
    listen 80;
    server_name 72.56.79.153;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 72.56.79.153;
    
    ssl_certificate /etc/ssl/certs/pentest.crt;
    ssl_certificate_key /etc/ssl/private/pentest.key;
    
    root /root/shannon/template/dist;
    
    # Статические assets - используем rewrite для перенаправления на /assets/
    location ^~ /app/assets/ {
        rewrite ^/app/assets/(.*)$ /assets/$1 break;
    }
    
    # Frontend SPA - все запросы к /app/* должны возвращать index.html
    location /app {
        try_files $uri $uri/ /app/index.html;
    }
    
    # Корневой путь - редирект на /app
    location = / {
        return 301 /app/;
    }
    
    # API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }
    
    # WebSocket
    location /socket.io {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
"""
        
        print("\n1. ОБНОВЛЕНИЕ КОНФИГУРАЦИИ:")
        ssh_exec(ssh, f"cat > /etc/nginx/sites-available/pentest << 'NGINX_EOF'\n{nginx_config}\nNGINX_EOF")
        print("  [OK] Конфигурация обновлена")
        
        # Проверяем синтаксис
        print("\n2. ПРОВЕРКА СИНТАКСИСА:")
        success, output, error = ssh_exec(ssh, "nginx -t")
        if success:
            print("  [OK] Синтаксис правильный")
        else:
            print(f"  [ERROR] Ошибка: {error}")
            return
        
        # Перезагружаем Nginx
        print("\n3. ПЕРЕЗАГРУЗКА NGINX:")
        ssh_exec(ssh, "systemctl reload nginx")
        print("  [OK] Nginx перезагружен")
        
        # Проверяем редирект
        print("\n4. ПРОВЕРКА РЕДИРЕКТА:")
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        try:
            response = requests.get("https://72.56.79.153/", verify=False, timeout=5, allow_redirects=False)
            if response.status_code in [301, 302, 307, 308]:
                location = response.headers.get('Location', '')
                print(f"  ✓ Редирект работает: / -> {location}")
            else:
                print(f"  ⚠ Статус редиректа: {response.status_code}")
        except Exception as e:
            print(f"  ⚠ Ошибка проверки: {str(e)}")
        
        print("\n" + "="*70)
        print("ГОТОВО!")
        print("="*70)
        print("\nТеперь попробуйте открыть:")
        print("  https://72.56.79.153/")
        print("  или")
        print("  https://72.56.79.153/app/")
        print("\nЕсли страница все еще не открывается:")
        print("1. Примите самоподписанный SSL сертификат")
        print("2. Откройте консоль браузера (F12) и проверьте ошибки")
        print("3. Попробуйте режим инкогнито")
        print("="*70)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()


