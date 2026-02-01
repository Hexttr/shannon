#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Форматирование файла через prettier и пересборка
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
    print("ФОРМАТИРОВАНИЕ И ПЕРЕСБОРКА")
    print("="*70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Форматируем файл через prettier
        print("\n1. ФОРМАТИРОВАНИЕ ФАЙЛА:")
        print("-" * 70)
        success, format_output, error = ssh_exec(ssh, f"cd {FRONTEND_DIR} && npx prettier --write src/pages/Pentests.tsx 2>&1")
        if success:
            print("  [OK] Файл отформатирован")
        else:
            print(f"  [WARNING] Ошибка форматирования: {format_output[:200]}")
        
        # Проверяем форматированный файл
        print("\n2. ПРОВЕРКА ФОРМАТИРОВАННОГО ФАЙЛА:")
        print("-" * 70)
        success2, check_output, error2 = ssh_exec(ssh, f"head -100 {FRONTEND_DIR}/src/pages/Pentests.tsx | tail -20")
        print(check_output)
        
        # Пересобираем фронтенд
        print("\n3. ПЕРЕСБОРКА ФРОНТЕНДА:")
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
        print("\n4. ИСПРАВЛЕНИЕ ПУТЕЙ В INDEX.HTML:")
        print("-" * 70)
        success5, html_content, error5 = ssh_exec(ssh, f"cat {FRONTEND_DIR}/dist/index.html")
        if '/app/assets/' in html_content:
            fixed_html = html_content.replace('/app/assets/', '/assets/')
            ssh_exec(ssh, f"cat > {FRONTEND_DIR}/dist/index.html << 'HTML_EOF'\n{fixed_html}\nHTML_EOF")
            print("  [OK] Пути исправлены")
        else:
            print("  [OK] Пути уже правильные")
        
        # Устанавливаем права доступа
        print("\n5. УСТАНОВКА ПРАВ ДОСТУПА:")
        print("-" * 70)
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        print("  [OK] Права установлены")
        
        print("\n" + "="*70)
        print("ГОТОВО!")
        print("="*70)
        print("\nПопробуйте обновить страницу (Ctrl+F5) и проверить снова.")
        print("="*70)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()


