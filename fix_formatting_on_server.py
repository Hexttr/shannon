#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление форматирования Pentests.tsx на сервере
"""

import paramiko
import sys
import re

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
    print("ИСПРАВЛЕНИЕ ФОРМАТИРОВАНИЯ НА СЕРВЕРЕ")
    print("="*70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Читаем файл с сервера
        print("\n1. ЧТЕНИЕ ФАЙЛА С СЕРВЕРА:")
        print("-" * 70)
        success, server_content, error = ssh_exec(ssh, f"cat {FRONTEND_DIR}/src/pages/Pentests.tsx")
        print(f"  Размер файла: {len(server_content)} символов")
        
        # Исправляем форматирование - добавляем переносы строк после useQuery
        print("\n2. ИСПРАВЛЕНИЕ ФОРМАТИРОВАНИЯ:")
        print("-" * 70)
        
        # Исправляем сжатые useQuery - добавляем переносы строк после закрывающих скобок
        fixed_content = re.sub(
            r'(useQuery\(\{[^}]*\}\);)',
            lambda m: m.group(1) + '\n  ',
            server_content
        )
        
        # Исправляем сжатые const - добавляем переносы строк
        fixed_content = re.sub(
            r'(const [^=]+ = [^;]+;)',
            lambda m: m.group(1) + '\n  ',
            fixed_content
        )
        
        # Исправляем сжатые return - добавляем переносы строк
        fixed_content = re.sub(
            r'(return \([\s\S]*?\);)\s*(}\);)\s*(export)',
            r'\1\n\2\n\n\3',
            fixed_content,
            flags=re.DOTALL
        )
        
        # Загружаем исправленный файл
        print("\n3. ЗАГРУЗКА ИСПРАВЛЕННОГО ФАЙЛА:")
        print("-" * 70)
        sftp = ssh.open_sftp()
        try:
            with sftp.file(f'{FRONTEND_DIR}/src/pages/Pentests.tsx', 'w') as remote_file:
                remote_file.write(fixed_content)
            print("  [OK] Файл загружен")
        except Exception as e:
            print(f"  [ERROR] Ошибка загрузки: {e}")
            sftp.close()
            return
        sftp.close()
        
        # Проверяем загруженный файл
        print("\n4. ПРОВЕРКА ЗАГРУЖЕННОГО ФАЙЛА:")
        print("-" * 70)
        success2, check_output, error2 = ssh_exec(ssh, f"head -70 {FRONTEND_DIR}/src/pages/Pentests.tsx | tail -10")
        print(check_output)
        
        # Пересобираем фронтенд
        print("\n5. ПЕРЕСБОРКА ФРОНТЕНДА:")
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
        print("\n6. ИСПРАВЛЕНИЕ ПУТЕЙ В INDEX.HTML:")
        print("-" * 70)
        success5, html_content, error5 = ssh_exec(ssh, f"cat {FRONTEND_DIR}/dist/index.html")
        if '/app/assets/' in html_content:
            fixed_html = html_content.replace('/app/assets/', '/assets/')
            ssh_exec(ssh, f"cat > {FRONTEND_DIR}/dist/index.html << 'HTML_EOF'\n{fixed_html}\nHTML_EOF")
            print("  [OK] Пути исправлены")
        else:
            print("  [OK] Пути уже правильные")
        
        # Устанавливаем права доступа
        print("\n7. УСТАНОВКА ПРАВ ДОСТУПА:")
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



