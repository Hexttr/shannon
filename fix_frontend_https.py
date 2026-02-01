#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление проблемы с frontend на HTTPS
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
    print("ИСПРАВЛЕНИЕ FRONTEND НА HTTPS")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка наличия dist
        print("\n1. ПРОВЕРКА FRONTEND:")
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ 2>&1 | head -10")
        print(output)
        
        # 2. Проверка index.html
        print("\n2. ПРОВЕРКА INDEX.HTML:")
        success, output, error = ssh_exec(ssh, f"test -f {FRONTEND_DIR}/dist/index.html && echo 'EXISTS' || echo 'MISSING'")
        print(f"  index.html: {output.strip()}")
        
        # 3. Пересборка frontend
        print("\n3. ПЕРЕСБОРКА FRONTEND:")
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && cat > .env << 'EOFFRONTEND'\nVITE_API_URL=https://{SSH_HOST}/api\nEOFFRONTEND")
        print("  [OK] .env обновлен")
        
        success, output, error = ssh_exec(ssh, f"cd {FRONTEND_DIR} && npm run build 2>&1 | tail -10")
        print(output)
        
        # 4. Проверка прав доступа
        print("\n4. ПРОВЕРКА ПРАВ ДОСТУПА:")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist 2>&1 || chown -R root:root {FRONTEND_DIR}/dist")
        print("  [OK] Права обновлены")
        
        # 5. Проверка Nginx конфигурации
        print("\n5. ПРОВЕРКА NGINX:")
        success, output, error = ssh_exec(ssh, "nginx -t 2>&1")
        print(output)
        
        if "successful" in output.lower():
            ssh_exec(ssh, "systemctl reload nginx")
            print("  [OK] Nginx перезагружен")
        else:
            print(f"  [ERROR] Ошибка конфигурации")
        
        # 6. Тест доступа
        print("\n6. ТЕСТ ДОСТУПА:")
        time.sleep(2)
        success, output, error = ssh_exec(ssh, f"curl -k -s https://{SSH_HOST}/ | head -20")
        if "<!DOCTYPE html>" in output or "<html" in output.lower():
            print("  ✅ Frontend доступен")
            print(f"  Первые строки: {output[:200]}")
        else:
            print(f"  ⚠️  Ответ: {output[:300]}")
        
        print("\n" + "="*60)
        print("ИСПРАВЛЕНИЕ ЗАВЕРШЕНО")
        print("="*60)
        print(f"\n🌐 Ссылка для открытия в браузере:")
        print(f"   https://{SSH_HOST}")
        print(f"\n📋 Или скопируйте эту ссылку:")
        print(f"   https://{SSH_HOST}")
        print(f"\n🔐 Учетные данные:")
        print(f"   Логин: admin")
        print(f"   Пароль: admin")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()



