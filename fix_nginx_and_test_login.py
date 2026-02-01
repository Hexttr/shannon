#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление конфигурации Nginx и тестирование логина
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def test_https_login(conn):
    """Тестирует логин через HTTPS"""
    print("="*60)
    print("🔒 Тестирование логина через HTTPS...")
    print("="*60)
    
    curl_cmd = 'curl -s -k -X POST https://72.56.79.153/api/auth/login -H "Content-Type: application/json" -H "Accept: application/json" -d \'{"username":"admin","password":"admin"}\''
    
    output, error, code = conn.execute(curl_cmd)
    print(f"Exit code: {code}")
    print(f"Response: {output[:400] if output else 'No output'}")
    
    if output and 'token' in output:
        print("\n✅ Логин работает через HTTPS!")
        return True
    else:
        print("\n❌ Логин не работает через HTTPS")
        return False

def check_nginx_config(conn):
    """Проверяет конфигурацию Nginx"""
    print("\n" + "="*60)
    print("📋 Проверка конфигурации Nginx...")
    print("="*60)
    
    # Находим активный конфиг
    output, _, _ = conn.execute('ls -la /etc/nginx/sites-enabled/')
    print("Активные конфиги:")
    print(output)
    
    # Читаем конфиг
    output, _, _ = conn.execute('cat /etc/nginx/sites-enabled/default 2>/dev/null || cat /etc/nginx/sites-enabled/* 2>/dev/null | head -100')
    if output:
        print("\nТекущая конфигурация:")
        print(output[:1000])
    
    return output

def fix_nginx_config(conn):
    """Исправляет конфигурацию Nginx"""
    print("\n" + "="*60)
    print("🔧 Исправление конфигурации Nginx...")
    print("="*60)
    
    # Проверяем наличие файла
    output, _, _ = conn.execute('test -f /etc/nginx/sites-enabled/default && echo "exists" || echo "not-found"')
    
    if 'not-found' in output:
        # Ищем другие конфиги
        output, _, _ = conn.execute('ls /etc/nginx/sites-enabled/')
        print(f"Найденные конфиги: {output}")
    
    # Исправляем конфигурацию - убираем цикл rewrite
    fix_cmd = '''cat > /tmp/nginx_fix.conf << 'EOF'
server {
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

    # Frontend (SPA) - исправленная версия без циклов
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
        
        # CORS заголовки
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, Accept" always;
        
        if ($request_method = OPTIONS) {
            return 204;
        }
    }

    # Health check
    location /up {
        proxy_pass http://127.0.0.1:8000/up;
        proxy_set_header Host $host;
    }
}
EOF
'''
    
    conn.execute(fix_cmd)
    
    # Копируем конфиг
    conn.execute('cp /tmp/nginx_fix.conf /etc/nginx/sites-available/shannon')
    conn.execute('ln -sf /etc/nginx/sites-available/shannon /etc/nginx/sites-enabled/default')
    
    # Проверяем конфигурацию
    output, error, code = conn.execute('nginx -t')
    print(f"\nПроверка конфигурации Nginx:")
    print(output)
    
    if code == 0:
        print("✅ Конфигурация валидна")
        # Перезагружаем Nginx
        output, _, _ = conn.execute('systemctl reload nginx')
        print("✅ Nginx перезагружен")
        return True
    else:
        print("❌ Ошибка в конфигурации")
        print(error)
        return False

def main():
    """Главная функция"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        # Проверяем текущую конфигурацию
        check_nginx_config(conn)
        
        # Тестируем HTTPS логин
        if not test_https_login(conn):
            # Исправляем конфигурацию
            if fix_nginx_config(conn):
                # Тестируем снова
                print("\n" + "="*60)
                print("🔄 Повторное тестирование после исправления...")
                print("="*60)
                test_https_login(conn)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()

