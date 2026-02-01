#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка причин черного экрана
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
    print("ПРОВЕРКА ПРИЧИН ЧЕРНОГО ЭКРАНА")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверяем index.html
        print("\n1. ПРОВЕРКА INDEX.HTML:")
        success, html_content, error = ssh_exec(ssh, f"cat {FRONTEND_DIR}/dist/index.html")
        print(f"  Размер файла: {len(html_content)} байт")
        if '<div id="root"></div>' in html_content:
            print("  [OK] Элемент #root найден")
        else:
            print("  [ERROR] Элемент #root не найден!")
        
        # Проверяем пути к JS и CSS
        if '/assets/' in html_content:
            print("  [OK] Пути к assets правильные (/assets/)")
        elif '/app/assets/' in html_content:
            print("  [WARNING] Пути к assets неправильные (/app/assets/)")
        else:
            print("  [WARNING] Пути к assets не найдены")
        
        # 2. Проверяем, что JS файл доступен
        print("\n2. ПРОВЕРКА JS ФАЙЛА:")
        success2, js_files, error2 = ssh_exec(ssh, f"ls {FRONTEND_DIR}/dist/assets/*.js 2>&1 | head -1")
        if "No such file" in js_files:
            print("  [ERROR] JS файлы не найдены!")
        else:
            js_file = js_files.strip().split('\n')[0]
            print(f"  [OK] JS файл найден: {js_file.split('/')[-1]}")
            
            # Проверяем доступность через HTTP
            success3, http_check, error3 = ssh_exec(ssh, f"curl -k -I https://72.56.79.153/assets/{js_file.split('/')[-1]} 2>&1 | grep -E '(HTTP|content-type)'")
            print(f"  HTTP статус: {http_check}")
        
        # 3. Проверяем CSS файл
        print("\n3. ПРОВЕРКА CSS ФАЙЛА:")
        success4, css_files, error4 = ssh_exec(ssh, f"ls {FRONTEND_DIR}/dist/assets/*.css 2>&1 | head -1")
        if "No such file" in css_files:
            print("  [ERROR] CSS файлы не найдены!")
        else:
            css_file = css_files.strip().split('\n')[0]
            print(f"  [OK] CSS файл найден: {css_file.split('/')[-1]}")
        
        # 4. Проверяем App.tsx - basename
        print("\n4. ПРОВЕРКА APP.TSX:")
        success5, app_content, error5 = ssh_exec(ssh, f"grep -A 3 'const basename' {FRONTEND_DIR}/src/App.tsx")
        print(f"  {app_content}")
        
        # 5. Проверяем, что происходит при загрузке страницы
        print("\n5. ТЕСТ ЗАГРУЗКИ СТРАНИЦЫ:")
        success6, page_content, error6 = ssh_exec(ssh, "curl -k -s https://72.56.79.153/app/ | grep -E '(script|link)' | head -5")
        print(f"  Теги script/link: {page_content}")
        
        # 6. Проверяем конфигурацию Nginx для /app
        print("\n6. ПРОВЕРКА NGINX КОНФИГУРАЦИИ:")
        success7, nginx_config, error7 = ssh_exec(ssh, "grep -A 5 'location /app' /etc/nginx/sites-available/pentest | head -10")
        print(f"  {nginx_config}")
        
        print("\n" + "="*60)
        print("ДИАГНОСТИКА ЗАВЕРШЕНА")
        print("="*60)
        
        # Рекомендации
        print("\nВОЗМОЖНЫЕ ПРИЧИНЫ:")
        print("1. React Router basename не соответствует текущему пути")
        print("2. AuthContext застревает в loading состоянии")
        print("3. CSS не применяется (проверьте консоль браузера)")
        print("4. JavaScript ошибка, которая не показывается в консоли")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()


