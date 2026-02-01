#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление формата ответов API сервисов
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
    print("ИСПРАВЛЕНИЕ ФОРМАТА ОТВЕТОВ API")
    print("="*70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Загружаем исправленные файлы
        print("\n1. ЗАГРУЗКА ИСПРАВЛЕННЫХ ФАЙЛОВ:")
        print("-" * 70)
        
        # Используем SFTP для загрузки файлов
        sftp = ssh.open_sftp()
        
        # Загружаем serviceApi.ts
        try:
            with open('template/src/services/serviceApi.ts', 'rb') as f:
                sftp.putfo(f, f'{FRONTEND_DIR}/src/services/serviceApi.ts')
            print("  [OK] serviceApi.ts загружен")
        except Exception as e:
            print(f"  [ERROR] Ошибка загрузки serviceApi.ts: {e}")
            sftp.close()
            return
        
        # Загружаем pentestApi.ts
        try:
            with open('template/src/services/pentestApi.ts', 'rb') as f:
                sftp.putfo(f, f'{FRONTEND_DIR}/src/services/pentestApi.ts')
            print("  [OK] pentestApi.ts загружен")
        except Exception as e:
            print(f"  [ERROR] Ошибка загрузки pentestApi.ts: {e}")
            sftp.close()
            return
        
        sftp.close()
        
        # Проверяем файлы
        print("\n2. ПРОВЕРКА ЗАГРУЖЕННЫХ ФАЙЛОВ:")
        success1, content1, error1 = ssh_exec(ssh, f"grep -A 3 'getAll:' {FRONTEND_DIR}/src/services/serviceApi.ts | head -5")
        if 'response.data.data' in content1:
            print("  ✓ serviceApi.ts содержит правильный код")
        else:
            print("  ✗ serviceApi.ts НЕ содержит правильный код")
            print(f"  {content1}")
        
        success2, content2, error2 = ssh_exec(ssh, f"grep -A 3 'getAll:' {FRONTEND_DIR}/src/services/pentestApi.ts | head -5")
        if 'response.data.data' in content2:
            print("  ✓ pentestApi.ts содержит правильный код")
        else:
            print("  ✗ pentestApi.ts НЕ содержит правильный код")
            print(f"  {content2}")
        
        # Очищаем кэш и пересобираем
        print("\n3. ОЧИСТКА КЭША И ПЕРЕСБОРКА:")
        ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/node_modules/.vite")
        ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/dist")
        print("  [OK] Кэш очищен")
        
        print("  Запускаем сборку (это может занять 2-3 минуты)...")
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
        
        # Исправляем пути в index.html
        print("\n4. ИСПРАВЛЕНИЕ ПУТЕЙ В INDEX.HTML:")
        success3, html_content, error3 = ssh_exec(ssh, f"cat {FRONTEND_DIR}/dist/index.html")
        if '/app/assets/' in html_content:
            fixed_html = html_content.replace('/app/assets/', '/assets/')
            ssh_exec(ssh, f"cat > {FRONTEND_DIR}/dist/index.html << 'HTML_EOF'\n{fixed_html}\nHTML_EOF")
            print("  [OK] Пути исправлены")
        else:
            print("  [OK] Пути уже правильные")
        
        # Устанавливаем права доступа
        print("\n5. УСТАНОВКА ПРАВ ДОСТУПА:")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        print("  [OK] Права установлены")
        
        print("\n" + "="*70)
        print("ГОТОВО!")
        print("="*70)
        print("\nТеперь API сервисы правильно обрабатывают формат ответа Laravel.")
        print("Обновите страницу (Ctrl+F5) и проверьте работу.")
        print("="*70)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()



