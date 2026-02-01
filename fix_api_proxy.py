#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление проксирования API
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
    print("ИСПРАВЛЕНИЕ ПРОКСИРОВАНИЯ API")
    print("="*70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Обновляем конфигурацию Nginx с правильным проксированием
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
    
    # Статические assets
    location ^~ /app/assets/ {
        rewrite ^/app/assets/(.*)$ /assets/$1 break;
    }
    
    # Frontend SPA
    location /app {
        try_files $uri $uri/ /app/index.html;
    }
    
    # API - ВАЖНО: должен быть ПЕРЕД /app
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_cache_bypass $http_upgrade;
        
        # CORS заголовки
        add_header Access-Control-Allow-Origin $http_origin always;
        add_header Access-Control-Allow-Methods 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header Access-Control-Allow-Headers 'Authorization, Content-Type, Accept, Origin' always;
        add_header Access-Control-Allow-Credentials 'true' always;
        
        # Обработка OPTIONS запросов
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin $http_origin always;
            add_header Access-Control-Allow-Methods 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header Access-Control-Allow-Headers 'Authorization, Content-Type, Accept, Origin' always;
            add_header Access-Control-Allow-Credentials 'true' always;
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type 'text/plain charset=UTF-8';
            add_header Content-Length 0;
            return 204;
        }
        
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }
    
    # Корневой путь - редирект на /app
    location = / {
        return 301 /app/;
    }
}
"""
        
        print("\n1. ОБНОВЛЕНИЕ КОНФИГУРАЦИИ NGINX:")
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
        
        # Проверяем Laravel TrustProxies
        print("\n4. ПРОВЕРКА LARAVEL TRUSTPROXIES:")
        success2, trust_proxies, error2 = ssh_exec(ssh, "grep -A 5 'protected \$proxies' /root/shannon/backend-laravel/app/Http/Middleware/TrustProxies.php 2>&1 | head -10")
        if 'protected $proxies' in trust_proxies:
            print("  [OK] TrustProxies найден")
            print(f"  {trust_proxies}")
        else:
            print("  [WARNING] TrustProxies не найден или не настроен")
        
        # Проверяем CORS конфигурацию
        print("\n5. ПРОВЕРКА CORS КОНФИГУРАЦИИ:")
        success3, cors_config, error3 = ssh_exec(ssh, "grep -A 10 'allowed_origins' /root/shannon/backend-laravel/config/cors.php 2>&1 | head -15")
        print(cors_config)
        
        # Тестируем API
        print("\n6. ТЕСТИРОВАНИЕ API:")
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        try:
            response = requests.post(
                "https://72.56.79.153/api/auth/login",
                json={"username": "admin", "password": "admin"},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Origin": "https://72.56.79.153"
                },
                verify=False,
                timeout=5
            )
            print(f"  Статус: {response.status_code}")
            print(f"  CORS заголовки:")
            for header in ['Access-Control-Allow-Origin', 'Access-Control-Allow-Methods', 'Access-Control-Allow-Credentials']:
                value = response.headers.get(header, 'не найден')
                print(f"    {header}: {value}")
            
            if response.status_code == 200:
                print(f"  ✓ API работает корректно")
            else:
                print(f"  ✗ API вернул ошибку: {response.status_code}")
                print(f"    Ответ: {response.text[:200]}")
        except Exception as e:
            print(f"  ✗ Ошибка тестирования: {str(e)}")
        
        print("\n" + "="*70)
        print("ГОТОВО!")
        print("="*70)
        print("\nПопробуйте обновить страницу (Ctrl+F5) и войти снова.")
        print("Если проблема сохраняется, проверьте консоль браузера (F12).")
        print("="*70)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()



