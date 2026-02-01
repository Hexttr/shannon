#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление Nginx: убираем try_files из /app, чтобы не перехватывать assets
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
    print("="*60)
    print("ИСПРАВЛЕНИЕ NGINX: УБИРАЕМ TRY_FILES")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Убираем try_files из /app, чтобы не перехватывать assets
        nginx_config = """server {
    listen 80;
    server_name 72.56.79.153;
}

server {
    listen 443 ssl http2;
    server_name 72.56.79.153;
    
    ssl_certificate /etc/ssl/certs/pentest.crt;
    ssl_certificate_key /etc/ssl/private/pentest.key;
    
    # Статические assets - должен быть ПЕРЕД /app
    location /app/assets/ {
        alias /root/shannon/template/dist/assets/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # index.html для SPA
    location = /app/index.html {
        alias /root/shannon/template/dist/index.html;
    }
    
    # Frontend - статические файлы (БЕЗ try_files, чтобы не перехватывать assets)
    location /app {
        alias /root/shannon/template/dist;
        index index.html;
    }
    
    # Fallback для SPA routes - только если файл не найден
    location ~ ^/app/[^/]+$ {
        alias /root/shannon/template/dist/index.html;
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
    
    # Root redirect to /app
    location = / {
        return 301 /app;
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
        
        # Проверяем JS файл
        print("\n4. ПРОВЕРКА JS ФАЙЛА:")
        success, output, error = ssh_exec(ssh, "curl -k -I https://72.56.79.153/app/assets/index-fR8kCqPq-1769869492803.js 2>&1 | grep -E '(HTTP|content-type)'")
        print(f"  {output}")
        
        # Проверяем содержимое
        success2, output2, error2 = ssh_exec(ssh, "curl -k -s https://72.56.79.153/app/assets/index-fR8kCqPq-1769869492803.js | head -3")
        if "import" in output2 or "function" in output2 or "const" in output2 or "=>" in output2:
            print("  [OK] Файл содержит JavaScript код!")
        else:
            print(f"  [ERROR] Файл не содержит JS: {output2[:200]}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()



