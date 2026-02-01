#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка ошибки 500 на фронтенде
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
    print("ПРОВЕРКА ОШИБКИ 500 НА ФРОНТЕНДЕ")
    print("="*70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Проверяем логи Nginx
        print("\n1. ПРОВЕРКА ЛОГОВ NGINX:")
        print("-" * 70)
        success, nginx_error, error = ssh_exec(ssh, "tail -50 /var/log/nginx/error.log | grep -A 5 '500\\|pentest\\|app/home' | tail -30")
        print(nginx_error)
        
        # Проверяем логи доступа
        print("\n2. ПРОВЕРКА ЛОГОВ ДОСТУПА NGINX:")
        print("-" * 70)
        success2, nginx_access, error2 = ssh_exec(ssh, "tail -20 /var/log/nginx/access.log | grep 'pentest\\|500'")
        print(nginx_access)
        
        # Проверяем существование dist
        print("\n3. ПРОВЕРКА СУЩЕСТВОВАНИЯ DIST:")
        print("-" * 70)
        success3, dist_check, error3 = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ 2>&1 | head -10")
        print(dist_check)
        
        # Проверяем index.html
        print("\n4. ПРОВЕРКА INDEX.HTML:")
        print("-" * 70)
        success4, html_check, error4 = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/index.html 2>&1")
        print(html_check)
        
        if "No such file" in html_check:
            print("  ✗ index.html не найден!")
            print("\n5. ПЕРЕСБОРКА ФРОНТЕНДА:")
            print("-" * 70)
            ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/dist")
            print("  [OK] Старый dist удален")
            
            print("  Запускаем сборку...")
            stdin, stdout, stderr = ssh.exec_command(f"cd {FRONTEND_DIR} && npm run build 2>&1")
            output_lines = []
            while True:
                line = stdout.readline()
                if not line:
                    break
                output_lines.append(line)
                if len(output_lines) % 30 == 0:
                    print(f"  Собрано строк: {len(output_lines)}...")
            
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                print("  [OK] Сборка завершена")
            else:
                print(f"  [ERROR] Ошибка сборки")
                output = ''.join(output_lines)
                print(output[-1000:] if len(output) > 1000 else output)
                return
        
        # Проверяем содержимое index.html
        print("\n5. ПРОВЕРКА СОДЕРЖИМОГО INDEX.HTML:")
        print("-" * 70)
        success5, html_content, error5 = ssh_exec(ssh, f"head -20 {FRONTEND_DIR}/dist/index.html")
        print(html_content)
        
        # Проверяем пути в index.html
        print("\n6. ПРОВЕРКА ПУТЕЙ В INDEX.HTML:")
        print("-" * 70)
        success6, paths_check, error6 = ssh_exec(ssh, f"grep -o '/app/assets/[^\"']*' {FRONTEND_DIR}/dist/index.html | head -5")
        if paths_check.strip():
            print("  ⚠ Найдены пути /app/assets/ - нужно исправить")
            print(paths_check)
            # Исправляем пути
            ssh_exec(ssh, f"sed -i 's|/app/assets/|/assets/|g' {FRONTEND_DIR}/dist/index.html")
            print("  [OK] Пути исправлены")
        else:
            print("  ✓ Пути правильные")
        
        # Проверяем права доступа
        print("\n7. ПРОВЕРКА ПРАВ ДОСТУПА:")
        print("-" * 70)
        success7, perms_check, error7 = ssh_exec(ssh, f"ls -ld {FRONTEND_DIR}/dist")
        print(perms_check)
        
        # Устанавливаем правильные права
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        print("  [OK] Права установлены")
        
        # Проверяем конфигурацию Nginx
        print("\n8. ПРОВЕРКА КОНФИГУРАЦИИ NGINX:")
        print("-" * 70)
        success8, nginx_config, error8 = ssh_exec(ssh, "grep -A 10 'location /app' /etc/nginx/sites-available/pentest | head -15")
        print(nginx_config)
        
        # Перезагружаем Nginx
        print("\n9. ПЕРЕЗАГРУЗКА NGINX:")
        print("-" * 70)
        ssh_exec(ssh, "nginx -t")
        ssh_exec(ssh, "systemctl reload nginx")
        print("  [OK] Nginx перезагружен")
        
        print("\n" + "="*70)
        print("ГОТОВО!")
        print("="*70)
        print("\nПопробуйте обновить страницу (Ctrl+F5) и проверить снова.")
        print("="*70)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()


