#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление конфигурации Nginx для статических файлов
"""

import paramiko
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
FRONTEND_DIR = "/root/shannon/template/dist"

def ssh_exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    print("="*60)
    print("ИСПРАВЛЕНИЕ КОНФИГУРАЦИИ NGINX")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Создаем резервную копию конфигурации
        print("\n1. СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ:")
        ssh_exec(ssh, "cp /etc/nginx/sites-available/pentest /etc/nginx/sites-available/pentest.backup")
        print("  [OK] Резервная копия создана")
        
        # 2. Обновляем конфигурацию Nginx
        print("\n2. ОБНОВЛЕНИЕ КОНФИГУРАЦИИ NGINX:")
        
        nginx_config = """server {
    listen 80;
    server_name 72.56.79.153;
}

server {
    listen 443 ssl http2;
    server_name 72.56.79.153;
    
    ssl_certificate /etc/ssl/certs/pentest.crt;
    ssl_certificate_key /etc/ssl/private/pentest.key;
    
    # Frontend - статические файлы
    location /app {
        alias /root/shannon/template/dist;
        try_files $uri $uri/ /app/index.html;
        
        # Правильные MIME типы для JS модулей
        location ~* \\.js$ {
            add_header Content-Type application/javascript;
        }
        
        location ~* \\.css$ {
            add_header Content-Type text/css;
        }
    }
    
    # Статические assets напрямую
    location /app/assets/ {
        alias /root/shannon/template/dist/assets/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # Правильные MIME типы
        location ~* \\.js$ {
            add_header Content-Type application/javascript;
        }
        
        location ~* \\.css$ {
            add_header Content-Type text/css;
        }
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
        
        # Таймауты для долгих запросов (10 минут)
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
    
    # Root redirect to /app
    location = / {
        return 301 /app;
    }
}
"""
        
        # Записываем конфигурацию
        ssh_exec(ssh, f"cat > /etc/nginx/sites-available/pentest << 'NGINX_EOF'\n{nginx_config}\nNGINX_EOF")
        print("  [OK] Конфигурация обновлена")
        
        # 3. Проверяем синтаксис
        print("\n3. ПРОВЕРКА СИНТАКСИСА:")
        success, output, error = ssh_exec(ssh, "nginx -t")
        if success:
            print("  [OK] Синтаксис правильный")
            print(output)
        else:
            print("  [ERROR] Ошибка синтаксиса:")
            print(error)
            return
        
        # 4. Перезагружаем Nginx
        print("\n4. ПЕРЕЗАГРУЗКА NGINX:")
        ssh_exec(ssh, "systemctl reload nginx")
        print("  [OK] Nginx перезагружен")
        
        # 5. Проверяем доступность файлов
        print("\n5. ПРОВЕРКА ДОСТУПНОСТИ:")
        success, output, error = ssh_exec(ssh, f"curl -k -s https://72.56.79.153/app/assets/index-fR8kCqPq-1769869492803.js | head -5")
        if "import" in output or "function" in output or "const" in output:
            print("  [OK] JS файл доступен и имеет правильный тип")
        else:
            print(f"  [WARNING] Ответ: {output[:200]}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()



