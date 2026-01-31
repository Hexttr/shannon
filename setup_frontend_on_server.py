#!/usr/bin/env python3
"""
Скрипт для настройки Frontend на сервере
"""

import paramiko
import os

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
FRONTEND_DIR = "/root/shannon/template"

def main():
    print("="*60)
    print("НАСТРОЙКА FRONTEND НА СЕРВЕРЕ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка Node.js и npm
        print("\n1. ПРОВЕРКА ЗАВИСИМОСТЕЙ:")
        stdin, stdout, stderr = ssh.exec_command("node --version")
        node_version = stdout.read().decode('utf-8', errors='replace').strip()
        if node_version:
            print(f"  [OK] Node.js: {node_version}")
        else:
            print("  [ERROR] Node.js не установлен!")
            return
        
        stdin, stdout, stderr = ssh.exec_command("npm --version")
        npm_version = stdout.read().decode('utf-8', errors='replace').strip()
        if npm_version:
            print(f"  [OK] npm: {npm_version}")
        
        # 2. Настройка .env для frontend
        print("\n2. НАСТРОЙКА ОКРУЖЕНИЯ:")
        env_content = f"""# API URL для Laravel backend
VITE_API_URL=https://{SSH_HOST}/api
"""
        stdin, stdout, stderr = ssh.exec_command(f"cd {FRONTEND_DIR} && cat > .env << 'EOF'\n{env_content}\nEOF")
        print("  [OK] .env файл создан")
        
        # 3. Установка зависимостей
        print("\n3. УСТАНОВКА ЗАВИСИМОСТЕЙ:")
        stdin, stdout, stderr = ssh.exec_command(f"cd {FRONTEND_DIR} && npm install 2>&1")
        output = stdout.read().decode('utf-8', errors='replace')
        if "error" in output.lower():
            print(f"  [WARNING] Возможны ошибки:")
            print(output[-500:])
        else:
            print("  [OK] Зависимости установлены")
        
        # 4. Сборка frontend
        print("\n4. СБОРКА FRONTEND:")
        stdin, stdout, stderr = ssh.exec_command(f"cd {FRONTEND_DIR} && npm run build 2>&1")
        output = stdout.read().decode('utf-8', errors='replace')
        if "error" in output.lower():
            print(f"  [ERROR] Ошибка сборки:")
            print(output[-1000:])
        else:
            print("  [OK] Frontend собран")
        
        # 5. Настройка Nginx
        print("\n5. НАСТРОЙКА NGINX:")
        nginx_config = f"""server {{
    listen 80;
    listen [::]:80;
    server_name {SSH_HOST};

    root {FRONTEND_DIR}/dist;
    index index.html;

    # Frontend (SPA)
    location / {{
        try_files $uri $uri/ /index.html;
    }}

    # API проксирование к Laravel backend
    location /api {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    # Health check для Laravel
    location /up {{
        proxy_pass http://127.0.0.1:8000/up;
        proxy_set_header Host $host;
    }}
}}
"""
        
        stdin, stdout, stderr = ssh.exec_command(f"cat > /etc/nginx/sites-available/shannon << 'EOF'\n{nginx_config}\nEOF")
        ssh.exec_command("ln -sf /etc/nginx/sites-available/shannon /etc/nginx/sites-enabled/shannon")
        ssh.exec_command("nginx -t && systemctl reload nginx")
        print("  [OK] Nginx настроен")
        
        print("\n" + "="*60)
        print("НАСТРОЙКА ЗАВЕРШЕНА")
        print("="*60)
        print(f"\nFrontend доступен на: http://{SSH_HOST}")
        print(f"API доступен на: http://{SSH_HOST}/api")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

