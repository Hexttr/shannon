#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление API URL в frontend и пересборка
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
    print("ИСПРАВЛЕНИЕ API URL В FRONTEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Обновление .env
        print("\n1. ОБНОВЛЕНИЕ .ENV:")
        env_content = f"VITE_API_URL=https://{SSH_HOST}/api\n"
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && cat > .env << 'EOFFRONTEND'\n{env_content}EOFFRONTEND")
        print("  [OK] .env обновлен")
        
        # 2. Проверка текущего .env
        print("\n2. ПРОВЕРКА .ENV:")
        success, output, error = ssh_exec(ssh, f"cat {FRONTEND_DIR}/.env")
        print(output)
        
        # 3. Пересборка frontend
        print("\n3. ПЕРЕСБОРКА FRONTEND:")
        print("  Это может занять несколько минут...")
        success, output, error = ssh_exec(ssh, f"cd {FRONTEND_DIR} && /usr/bin/npm run build 2>&1")
        if "built in" in output.lower() or "dist" in output.lower() or "vite" in output.lower():
            print("  [OK] Frontend пересобран")
            print(f"  {output[-300:]}")
        else:
            print(f"  [WARNING] Вывод: {output[-500:]}")
        
        # 4. Проверка собранного файла
        print("\n4. ПРОВЕРКА СОБРАННОГО КОДА:")
        success, output, error = ssh_exec(ssh, f"grep -r 'VITE_API_URL' {FRONTEND_DIR}/dist/ 2>&1 | head -3")
        if output:
            print(f"  Найдено: {output[:200]}")
        
        # Проверка встроенного API URL
        success, output, error = ssh_exec(ssh, f"grep -o 'https://72.56.79.153/api' {FRONTEND_DIR}/dist/assets/*.js 2>&1 | head -1")
        if output:
            print(f"  [OK] API URL найден в собранном коде")
        else:
            print("  [WARNING] API URL не найден в собранном коде")
        
        # 5. Перезагрузка Nginx
        print("\n5. ПЕРЕЗАГРУЗКА NGINX:")
        ssh_exec(ssh, "systemctl reload nginx")
        time.sleep(2)
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nПопробуйте войти снова:")
        print(f"  URL: https://{SSH_HOST}")
        print(f"  Логин: admin")
        print(f"  Пароль: admin")
        print(f"\nЕсли проблема сохраняется:")
        print(f"  1. Очистите кэш браузера (Ctrl+Shift+Delete)")
        print(f"  2. Откройте консоль браузера (F12)")
        print(f"  3. Проверьте, какой URL используется для запроса")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

