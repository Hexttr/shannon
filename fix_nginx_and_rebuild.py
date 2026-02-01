#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление Nginx и пересборка фронтенда
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
    print("="*70)
    print("ИСПРАВЛЕНИЕ NGINX И ПЕРЕСБОРКА ФРОНТЕНДА")
    print("="*70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Исправляем конфигурацию Nginx
        print("\n1. ИСПРАВЛЕНИЕ КОНФИГУРАЦИИ NGINX:")
        print("-" * 70)
        
        # Читаем текущую конфигурацию
        success, nginx_config, error = ssh_exec(ssh, "cat /etc/nginx/sites-available/pentest")
        print("  Текущая конфигурация:")
        print(nginx_config[:500])
        
        # Исправляем конфигурацию - убираем циклические редиректы
        fixed_nginx = """server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name 72.56.79.153;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    root /root/shannon/template/dist;
    index index.html;

    # API прокси
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Статические файлы
    location /assets {
        alias /root/shannon/template/dist/assets;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Favicon
    location = /favicon.ico {
        alias /root/shannon/template/dist/favicon.ico;
        access_log off;
    }

    # SPA routing - все остальные запросы на index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Отдельная обработка для /app
    location /app {
        alias /root/shannon/template/dist;
        try_files $uri $uri/ /index.html;
    }
}
"""
        
        ssh_exec(ssh, f"cat > /etc/nginx/sites-available/pentest << 'NGINX_EOF'\n{fixed_nginx}\nNGINX_EOF")
        print("  [OK] Конфигурация обновлена")
        
        # Проверяем конфигурацию
        success2, nginx_test, error2 = ssh_exec(ssh, "nginx -t")
        if success2:
            print("  [OK] Конфигурация валидна")
            ssh_exec(ssh, "systemctl reload nginx")
            print("  [OK] Nginx перезагружен")
        else:
            print(f"  [ERROR] Ошибка конфигурации: {nginx_test}")
            return
        
        # Исправляем файл Pentests.tsx - восстанавливаем форматирование
        print("\n2. ИСПРАВЛЕНИЕ PENTESTS.TSX:")
        print("-" * 70)
        
        # Используем git для восстановления файла
        success3, git_status, error3 = ssh_exec(ssh, f"cd {FRONTEND_DIR} && git status src/pages/Pentests.tsx")
        print(f"  Git статус: {git_status[:200]}")
        
        # Пробуем восстановить из git
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && git checkout HEAD -- src/pages/Pentests.tsx 2>&1")
        print("  [OK] Файл восстановлен из git")
        
        # Загружаем исправленный файл с локальной машины
        print("\n3. ЗАГРУЗКА ИСПРАВЛЕННОГО ФАЙЛА:")
        print("-" * 70)
        try:
            with open('template/src/pages/Pentests.tsx', 'r', encoding='utf-8') as f:
                local_content = f.read()
            
            # Загружаем через SFTP
            sftp = ssh.open_sftp()
            with sftp.file(f'{FRONTEND_DIR}/src/pages/Pentests.tsx', 'w') as remote_file:
                remote_file.write(local_content)
            sftp.close()
            print("  [OK] Файл загружен")
        except Exception as e:
            print(f"  [ERROR] Ошибка загрузки: {e}")
            return
        
        # Пересобираем фронтенд
        print("\n4. ПЕРЕСБОРКА ФРОНТЕНДА:")
        print("-" * 70)
        ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/dist")
        print("  [OK] Старый dist удален")
        
        print("  Запускаем сборку (это может занять 2-3 минуты)...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {FRONTEND_DIR} && npm run build 2>&1")
        output_lines = []
        error_lines = []
        
        while True:
            line = stdout.readline()
            if not line:
                break
            output_lines.append(line)
            if len(output_lines) % 30 == 0:
                print(f"  Собрано строк: {len(output_lines)}...")
        
        while True:
            line = stderr.readline()
            if not line:
                break
            error_lines.append(line)
        
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("  [OK] Сборка завершена")
        else:
            print(f"  [ERROR] Ошибка сборки")
            output = ''.join(output_lines)
            errors = ''.join(error_lines)
            print(output[-1500:] if len(output) > 1500 else output)
            if errors:
                print("\n  Ошибки:")
                print(errors[-500:] if len(errors) > 500 else errors)
            return
        
        # Исправляем пути в index.html
        print("\n5. ИСПРАВЛЕНИЕ ПУТЕЙ В INDEX.HTML:")
        print("-" * 70)
        success5, html_content, error5 = ssh_exec(ssh, f"cat {FRONTEND_DIR}/dist/index.html")
        if '/app/assets/' in html_content:
            fixed_html = html_content.replace('/app/assets/', '/assets/')
            ssh_exec(ssh, f"cat > {FRONTEND_DIR}/dist/index.html << 'HTML_EOF'\n{fixed_html}\nHTML_EOF")
            print("  [OK] Пути исправлены")
        else:
            print("  [OK] Пути уже правильные")
        
        # Устанавливаем права доступа
        print("\n6. УСТАНОВКА ПРАВ ДОСТУПА:")
        print("-" * 70)
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        print("  [OK] Права установлены")
        
        # Финальная перезагрузка Nginx
        print("\n7. ФИНАЛЬНАЯ ПЕРЕЗАГРУЗКА NGINX:")
        print("-" * 70)
        ssh_exec(ssh, "systemctl reload nginx")
        print("  [OK] Nginx перезагружен")
        
        print("\n" + "="*70)
        print("ГОТОВО!")
        print("="*70)
        print("\nТеперь фронтенд должен работать корректно.")
        print("Обновите страницу (Ctrl+F5) и попробуйте снова.")
        print("="*70)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()



