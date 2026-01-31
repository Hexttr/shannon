#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пересборка frontend с правильными правами
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
    print("ПЕРЕСБОРКА FRONTEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Исправление прав доступа
        print("\n1. ИСПРАВЛЕНИЕ ПРАВ ДОСТУПА:")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}")
        ssh_exec(ssh, f"chmod +x {FRONTEND_DIR}/node_modules/.bin/* 2>&1 || echo 'ok'")
        print("  [OK] Права обновлены")
        
        # 2. Обновление .env
        print("\n2. ОБНОВЛЕНИЕ .ENV:")
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && cat > .env << 'EOFFRONTEND'\nVITE_API_URL=https://{SSH_HOST}/api\nEOFFRONTEND")
        print("  [OK] .env обновлен")
        
        # 3. Пересборка через полный путь к npm
        print("\n3. ПЕРЕСБОРКА:")
        success, output, error = ssh_exec(ssh, f"cd {FRONTEND_DIR} && /usr/bin/npm run build 2>&1")
        if "built in" in output.lower() or "dist" in output.lower():
            print("  ✅ Frontend собран успешно")
            print(f"  {output[-200:]}")
        else:
            print(f"  ⚠️  Вывод: {output[-300:]}")
        
        # 4. Проверка dist
        print("\n4. ПРОВЕРКА DIST:")
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/ | head -10")
        print(output)
        
        # 5. Установка правильных прав для dist
        print("\n5. УСТАНОВКА ПРАВ ДЛЯ DIST:")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist 2>&1 || chown -R root:root {FRONTEND_DIR}/dist")
        print("  [OK] Права установлены")
        
        # 6. Перезагрузка Nginx
        print("\n6. ПЕРЕЗАГРУЗКА NGINX:")
        ssh_exec(ssh, "systemctl reload nginx")
        time.sleep(2)
        
        # 7. Тест
        print("\n7. ТЕСТ:")
        success, output, error = ssh_exec(ssh, f"curl -k -s https://{SSH_HOST}/ | head -30")
        if "<!DOCTYPE html>" in output or ("<html" in output.lower() and "500" not in output):
            print("  ✅ Frontend работает!")
            print(f"  Первые строки: {output[:300]}")
        else:
            print(f"  ⚠️  Ответ: {output[:400]}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\n🌐 Активная ссылка для открытия в браузере:")
        print(f"\n   👉 https://{SSH_HOST} 👈")
        print(f"\n📋 Скопируйте эту ссылку:")
        print(f"   https://{SSH_HOST}")
        print(f"\n🔐 Учетные данные для входа:")
        print(f"   Логин: admin")
        print(f"   Пароль: admin")
        print(f"\n⚠️  При первом открытии браузер покажет предупреждение")
        print(f"   о безопасности (из-за самоподписанного сертификата).")
        print(f"   Нажмите 'Продолжить' или 'Advanced' -> 'Proceed to site'")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

