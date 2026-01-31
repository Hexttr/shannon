#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление конфигурации Nginx
"""

import paramiko
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
FRONTEND_DIR = "/root/shannon/template"

def ssh_exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    print("="*60)
    print("ИСПРАВЛЕНИЕ NGINX")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Создание правильной конфигурации Nginx
        print("\n1. СОЗДАНИЕ КОНФИГУРАЦИИ NGINX:")
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
        ssh_exec(ssh, "rm -f /etc/nginx/sites-enabled/default")
        
        # 2. Проверка конфигурации
        print("\n2. ПРОВЕРКА КОНФИГУРАЦИИ:")
        success, output, error = ssh_exec(ssh, "nginx -t 2>&1")
        if "successful" in output.lower():
            print("  [OK] Конфигурация валидна")
            ssh_exec(ssh, "systemctl reload nginx")
            print("  [OK] Nginx перезагружен")
        else:
            print(f"  [ERROR] Ошибка: {output}")
        
        # 3. Проверка API
        print("\n3. ПРОВЕРКА API:")
        import time
        time.sleep(2)
        success, output, error = ssh_exec(ssh, f"curl -s http://{SSH_HOST}/api/auth/login -X POST -H 'Content-Type: application/json' -d '{{\"username\":\"test\",\"password\":\"test\"}}'")
        print(f"  Ответ: {output[:300]}")
        
        if "validation" in output.lower() or "username" in output.lower() or "password" in output.lower():
            print("  [OK] API работает!")
        elif "html" in output.lower():
            print("  [WARNING] Получен HTML вместо JSON")
        else:
            print(f"  [INFO] Ответ: {output[:200]}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nПриложение: http://{SSH_HOST}")
        print(f"Логин: admin")
        print(f"Пароль: admin")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

