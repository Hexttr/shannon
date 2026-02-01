#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пересборка фронтенда с исправлениями
"""

import paramiko
import sys
import time

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
    print("ПЕРЕСБОРКА ФРОНТЕНДА")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Удаляем старый dist
        print("\n1. УДАЛЕНИЕ СТАРОГО DIST:")
        ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/dist")
        print("  [OK] Старый dist удален")
        
        # 2. Собираем фронтенд
        print("\n2. СБОРКА ФРОНТЕНДА:")
        print("  Это может занять 2-3 минуты...")
        # Запускаем сборку в фоне
        stdin, stdout, stderr = ssh.exec_command(f"cd {FRONTEND_DIR} && npm run build 2>&1")
        # Ждем завершения
        output_lines = []
        while True:
            line = stdout.readline()
            if not line:
                break
            output_lines.append(line)
            if len(output_lines) % 10 == 0:
                print(f"  Собрано строк: {len(output_lines)}...")
        
        exit_status = stdout.channel.recv_exit_status()
        output = ''.join(output_lines)
        
        if exit_status == 0:
            print("  [OK] Сборка завершена")
        else:
            print(f"  [ERROR] Ошибка сборки:")
            print(output[-500:])  # Последние 500 символов
            return
        
        # 3. Проверяем dist
        print("\n3. ПРОВЕРКА DIST:")
        success, dist_check, error = ssh_exec(ssh, f"ls {FRONTEND_DIR}/dist/assets/*.js 2>&1 | head -1")
        if "No such file" in dist_check:
            print(f"  [ERROR] dist не создан!")
            return
        else:
            print(f"  [OK] dist создан: {dist_check.split('/')[-1]}")
        
        # 4. Исправляем пути в index.html
        print("\n4. ИСПРАВЛЕНИЕ ПУТЕЙ В INDEX.HTML:")
        success2, html_content, error2 = ssh_exec(ssh, f"cat {FRONTEND_DIR}/dist/index.html")
        if '/app/assets/' in html_content:
            fixed_html = html_content.replace('/app/assets/', '/assets/')
            ssh_exec(ssh, f"cat > {FRONTEND_DIR}/dist/index.html << 'HTML_EOF'\n{fixed_html}\nHTML_EOF")
            print("  [OK] Пути исправлены")
        else:
            print("  [OK] Пути уже правильные")
        
        # 5. Устанавливаем права доступа
        print("\n5. УСТАНОВКА ПРАВ ДОСТУПА:")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        print("  [OK] Права установлены")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print("\nОбновите страницу в браузере (Ctrl+F5) и проверьте работу.")
        print("Если проблема сохраняется, откройте консоль браузера (F12) и проверьте ошибки.")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
