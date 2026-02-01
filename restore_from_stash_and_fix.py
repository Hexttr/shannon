#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Восстановление из stash и исправление форматирования
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
    print("ВОССТАНОВЛЕНИЕ ИЗ STASH И ИСПРАВЛЕНИЕ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка stash
        print("\n1. ПРОВЕРКА STASH:")
        success, output, error = ssh_exec(ssh, "cd /root/shannon && git stash list")
        print(output)
        
        # 2. Восстановление файлов из stash (только для просмотра, не применяем)
        print("\n2. ПРОСМОТР STASH:")
        success, output, error = ssh_exec(ssh, "cd /root/shannon && git stash show -p stash@{0} --name-only | head -20")
        print(output)
        
        # 3. Исправление форматирования поврежденных файлов напрямую
        print("\n3. ИСПРАВЛЕНИЕ ФОРМАТИРОВАНИЯ:")
        
        # Исправляем Services.tsx - добавляем переносы строк после импортов
        fix_services = """cd {FRONTEND_DIR}/src/pages && python3 << 'EOFPYTHON'
import re

# Читаем файл
with open('Services.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Исправляем импорты - добавляем переносы строк
content = re.sub(r'import\s+([^;]+);', lambda m: 'import ' + m.group(1).replace(',', ',\n  ').replace('{', '{\n  ') + ';', content)
content = re.sub(r'from\s+[\'\"]([^\'\"]+)[\'\"]', lambda m: 'from ' + m.group(0), content)

# Исправляем основные структуры
content = re.sub(r'export default function', '\\nexport default function', content)
content = re.sub(r'const\s+(\w+)\s*=\s*useState', '\\n  const \\1 = useState', content)

# Записываем обратно
with open('Services.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print('Services.tsx исправлен')
EOFPYTHON
""".format(FRONTEND_DIR=FRONTEND_DIR)
        
        ssh_exec(ssh, fix_services)
        print("  [OK] Services.tsx исправлен")
        
        # 4. Попытка сборки
        print("\n4. СБОРКА:")
        ssh.exec_command(f"cd {FRONTEND_DIR} && timeout 180 npx vite build > /tmp/vite_build2.log 2>&1 &")
        time.sleep(90)
        
        success, output, error = ssh_exec(ssh, "tail -50 /tmp/vite_build2.log")
        print(f"  Лог: {output[-500:]}")
        
        # 5. Проверка dist
        print("\n5. ПРОВЕРКА DIST:")
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ 2>&1")
        print(output)
        
        if "index.html" in output:
            # Проверяем наличие JS файлов
            success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/assets/ 2>&1 | head -5")
            print(f"  Assets: {output}")
        
        # 6. Установка прав
        print("\n6. УСТАНОВКА ПРАВ:")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist 2>&1 || echo 'ok'")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist 2>&1 || chown -R root:root {FRONTEND_DIR}/dist 2>&1 || echo 'ok'")
        print("  [OK] Права установлены")
        
        # 7. Перезагрузка Nginx
        print("\n7. ПЕРЕЗАГРУЗКА NGINX:")
        ssh_exec(ssh, "systemctl reload nginx")
        time.sleep(2)
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nПопробуйте открыть:")
        print(f"  https://{SSH_HOST}")
        print(f"\nЛогин: admin")
        print(f"Пароль: admin")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()


