#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальное исправление путей в index.html
"""

import paramiko
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def ssh_exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    print("="*60)
    print("ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ПУТЕЙ В INDEX.HTML")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Используем sed для замены
        print("\n1. ЗАМЕНА ПУТЕЙ ЧЕРЕЗ SED:")
        success, output, error = ssh_exec(ssh, "sed -i 's|/app/assets/|/assets/|g' /root/shannon/template/dist/index.html")
        if success:
            print("  [OK] Пути заменены")
        else:
            print(f"  [ERROR] Ошибка: {error}")
        
        # Проверяем результат
        print("\n2. ПРОВЕРКА РЕЗУЛЬТАТА:")
        success2, output2, error2 = ssh_exec(ssh, "grep -o '/assets/' /root/shannon/template/dist/index.html")
        if '/assets/' in output2:
            print("  [OK] Пути исправлены!")
            print(f"  Найденные пути: {output2}")
        else:
            print("  [WARNING] Пути не найдены")
        
        # Проверяем через браузер
        print("\n3. ПРОВЕРКА ЧЕРЕЗ HTTP:")
        success3, output3, error3 = ssh_exec(ssh, "curl -k -s https://72.56.79.153/app/ | grep -o 'src=\"[^\"]*\"' | head -2")
        print(f"  Script tags: {output3}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print("\nТеперь обновите страницу в браузере (Ctrl+F5) и проверьте, работает ли приложение.")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()


