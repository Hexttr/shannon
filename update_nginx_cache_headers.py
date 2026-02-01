#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновление конфигурации Nginx для отключения кэширования index.html
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def update_nginx():
    """Обновляет конфигурацию Nginx"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔧 Обновление конфигурации Nginx...")
        print("="*60)
        
        nginx_config = """server {
    listen 80;
    listen [::]:80;
    server_name 72.56.79.153;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name 72.56.79.153;

    ssl_certificate /etc/nginx/ssl/72.56.79.153.crt;
    ssl_certificate_key /etc/nginx/ssl/72.56.79.153.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    root /root/shannon/template/dist;
    index index.html;

    # Отключаем кэширование для index.html
    location = /index.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
        try_files $uri =404;
    }

    # Кэшируем статические файлы (JS, CSS)
    location ~* \\.(js|css)$ {
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    # Основной location для SPA
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API проксирование к Laravel backend
    location /api {
        proxy_pass http://127.0.0.1:8000/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_read_timeout 300s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
    }

    # Health check
    location /up {
        proxy_pass http://127.0.0.1:8000/up;
        proxy_set_header Host $host;
    }
}
"""
        
        # Сохраняем конфигурацию
        conn.execute(f'cat > /tmp/nginx_shannon_new.conf << \'NGINX_EOF\'\n{nginx_config}\nNGINX_EOF')
        conn.execute('cp /tmp/nginx_shannon_new.conf /etc/nginx/sites-available/shannon')
        
        # Проверяем конфигурацию
        print("\nПроверка конфигурации...")
        output, error, code = conn.execute('nginx -t')
        print(output)
        
        if code == 0:
            print("✅ Конфигурация валидна")
            # Перезагружаем Nginx
            conn.execute('systemctl reload nginx')
            print("✅ Nginx перезагружен")
        else:
            print(f"❌ Ошибка в конфигурации: {error}")
            return False
        
        print("\n" + "="*60)
        print("✅ Конфигурация Nginx обновлена!")
        print("="*60)
        print("\n💡 Теперь:")
        print("   - index.html не будет кэшироваться")
        print("   - JS/CSS файлы будут кэшироваться")
        print("   - Обновите страницу в браузере (Ctrl+F5)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    update_nginx()

