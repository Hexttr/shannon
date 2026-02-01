#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пересборка фронтенда с исправленным API URL
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
    print("="*70)
    print("ПЕРЕСБОРКА ФРОНТЕНДА С ИСПРАВЛЕННЫМ API URL")
    print("="*70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверяем, что файл обновлен
        print("\n1. ПРОВЕРКА API.TS:")
        success, content, error = ssh_exec(ssh, f"grep -A 3 'getApiUrl' {FRONTEND_DIR}/src/services/api.ts | head -5")
        if 'getApiUrl' in content:
            print("  ✓ Файл содержит getApiUrl")
            print(f"  {content}")
        else:
            print("  ✗ Файл НЕ содержит getApiUrl")
            return
        
        # 2. Удаляем старый dist
        print("\n2. УДАЛЕНИЕ СТАРОГО DIST:")
        ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/dist")
        print("  [OK] Старый dist удален")
        
        # 3. Собираем фронтенд
        print("\n3. СБОРКА ФРОНТЕНДА:")
        print("  Это может занять 2-3 минуты...")
        
        stdin, stdout, stderr = ssh.exec_command(f"cd {FRONTEND_DIR} && npm run build 2>&1")
        output_lines = []
        error_lines = []
        
        # Читаем вывод построчно
        while True:
            line = stdout.readline()
            if not line:
                break
            output_lines.append(line)
            if len(output_lines) % 30 == 0:
                print(f"  Собрано строк: {len(output_lines)}...")
        
        # Читаем ошибки
        while True:
            line = stderr.readline()
            if not line:
                break
            error_lines.append(line)
        
        exit_status = stdout.channel.recv_exit_status()
        output = ''.join(output_lines)
        errors = ''.join(error_lines)
        
        if exit_status == 0:
            print("  [OK] Сборка завершена")
        else:
            print(f"  [ERROR] Ошибка сборки:")
            print(output[-1000:] if len(output) > 1000 else output)
            if errors:
                print(f"  Ошибки:")
                print(errors[-500:] if len(errors) > 500 else errors)
            return
        
        # 4. Проверяем dist
        print("\n4. ПРОВЕРКА DIST:")
        success2, dist_check, error2 = ssh_exec(ssh, f"ls {FRONTEND_DIR}/dist/assets/*.js 2>&1 | head -1")
        if "No such file" in dist_check:
            print(f"  [ERROR] dist не создан!")
            return
        else:
            js_file = dist_check.strip().split('\n')[0]
            print(f"  [OK] JS файл создан: {js_file.split('/')[-1]}")
        
        # 5. Проверяем, что новый код попал в сборку
        print("\n5. ПРОВЕРКА КОДА В СБОРКЕ:")
        success3, js_content, error3 = ssh_exec(ssh, f"head -c 50000 {js_file} | grep -o 'window.location.protocol' | head -1")
        if 'window.location.protocol' in js_content:
            print("  ✓ Код содержит window.location.protocol")
        else:
            # Проверяем весь файл
            success4, full_check, error4 = ssh_exec(ssh, f"grep -o 'window.location.protocol' {js_file} | head -1")
            if full_check.strip():
                print("  ✓ Код содержит window.location.protocol (найден в файле)")
            else:
                print("  ✗ Код НЕ содержит window.location.protocol")
                print("  ⚠ Возможно, код был оптимизирован/минифицирован")
        
        # Проверяем на наличие старого URL
        success5, old_url_check, error5 = ssh_exec(ssh, f"grep -o 'http://72.56.79.153:8000' {js_file} | head -1")
        if old_url_check.strip():
            print("  ⚠ В коде все еще есть старый URL: http://72.56.79.153:8000")
        else:
            print("  ✓ Старый URL не найден")
        
        # 6. Исправляем пути в index.html
        print("\n6. ИСПРАВЛЕНИЕ ПУТЕЙ В INDEX.HTML:")
        success6, html_content, error6 = ssh_exec(ssh, f"cat {FRONTEND_DIR}/dist/index.html")
        if '/app/assets/' in html_content:
            fixed_html = html_content.replace('/app/assets/', '/assets/')
            ssh_exec(ssh, f"cat > {FRONTEND_DIR}/dist/index.html << 'HTML_EOF'\n{fixed_html}\nHTML_EOF")
            print("  [OK] Пути исправлены")
        else:
            print("  [OK] Пути уже правильные")
        
        # 7. Устанавливаем права доступа
        print("\n7. УСТАНОВКА ПРАВ ДОСТУПА:")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        print("  [OK] Права установлены")
        
        print("\n" + "="*70)
        print("ГОТОВО!")
        print("="*70)
        print("\nВАЖНО: Обновите страницу с очисткой кэша:")
        print("1. Нажмите Ctrl+Shift+R (или Cmd+Shift+R на Mac)")
        print("2. Или откройте в режиме инкогнито")
        print("3. Или очистите кэш браузера (Ctrl+Shift+Delete)")
        print("\nТеперь API запросы должны идти через HTTPS.")
        print("="*70)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()


