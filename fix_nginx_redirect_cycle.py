#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление цикла редиректов в Nginx
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def fix_nginx_config():
    """Исправляет конфигурацию Nginx"""
    print("Проверка и исправление конфигурации Nginx...")
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # Проверка существования dist/index.html
        print("\n[1] Проверка существования dist/index.html:")
        output, error, code = conn.execute("ls -la /root/shannon/template/dist/index.html 2>&1")
        print(output)
        
        # Проверка структуры dist
        print("\n[2] Структура dist директории:")
        output, error, code = conn.execute("ls -la /root/shannon/template/dist/ | head -20")
        print(output)
        
        # Чтение текущей конфигурации
        print("\n[3] Текущая конфигурация Nginx:")
        output, error, code = conn.execute("cat /etc/nginx/sites-available/shannon")
        print(output)
        
        # Создание исправленной конфигурации
        nginx_config = """server {
    listen 80;
    listen [::]:80;
    server_name 72.56.79.153;
    
    # Редирект HTTP на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name 72.56.79.153;

    ssl_certificate /etc/nginx/ssl/72.56.79.153.crt;
    ssl_certificate_key /etc/nginx/ssl/72.56.79.153.key;
    
    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    root /root/shannon/template/dist;
    index index.html;

    # Логирование для отладки
    access_log /var/log/nginx/shannon_access.log;
    error_log /var/log/nginx/shannon_error.log;

    # Frontend (SPA) - исправленная конфигурация
    location / {
        try_files $uri $uri/ @fallback;
    }
    
    # Fallback для SPA маршрутов
    location @fallback {
        rewrite ^.*$ /index.html last;
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
    }

    # Health check
    location /up {
        proxy_pass http://127.0.0.1:8000/up;
        proxy_set_header Host $host;
    }
    
    # Статические файлы с кэшированием
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }
}
"""
        
        # Сохранение конфигурации
        print("\n[4] Сохранение исправленной конфигурации...")
        conn.execute(f"cat > /tmp/shannon_nginx.conf << 'NGINX_EOF'\n{nginx_config}\nNGINX_EOF")
        
        # Проверка синтаксиса
        print("\n[5] Проверка синтаксиса Nginx:")
        output, error, code = conn.execute("nginx -t -c /tmp/shannon_nginx.conf 2>&1")
        print(output)
        
        if code == 0:
            # Копирование конфигурации
            print("\n[6] Применение конфигурации...")
            conn.execute("cp /tmp/shannon_nginx.conf /etc/nginx/sites-available/shannon")
            
            # Перезагрузка Nginx
            print("\n[7] Перезагрузка Nginx...")
            output, error, code = conn.execute("nginx -t && systemctl reload nginx")
            print(output)
            if error:
                print(f"Ошибки: {error}")
            
            print("\n[OK] Конфигурация Nginx обновлена!")
            return True
        else:
            print("\n[ERROR] Ошибка в синтаксисе конфигурации!")
            return False

if __name__ == "__main__":
    success = fix_nginx_config()
    sys.exit(0 if success else 1)


