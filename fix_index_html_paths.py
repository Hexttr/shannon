#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление путей в index.html
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
    print("ИСПРАВЛЕНИЕ ПУТЕЙ В INDEX.HTML")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Читаем index.html
        print("\n1. ЧТЕНИЕ INDEX.HTML:")
        success, content, error = ssh_exec(ssh, "cat /root/shannon/template/dist/index.html")
        if not success:
            print(f"  [ERROR] Не удалось прочитать файл: {error}")
            return
        
        print(f"  [OK] Файл прочитан ({len(content)} байт)")
        
        # Заменяем пути
        print("\n2. ЗАМЕНА ПУТЕЙ:")
        # Заменяем /app/assets/ на /assets/
        new_content = content.replace('/app/assets/', '/assets/')
        
        if new_content == content:
            print("  [WARNING] Пути не изменены (возможно, уже правильные)")
        else:
            print("  [OK] Пути заменены")
        
        # Записываем обратно
        print("\n3. ЗАПИСЬ ОБНОВЛЕННОГО ФАЙЛА:")
        # Используем Python для записи файла
        ssh_exec(ssh, f"python3 -c \"import sys; content = '''{new_content.replace(chr(39), chr(39)+chr(39))}'''; open('/root/shannon/template/dist/index.html', 'w').write(content)\"")
        print("  [OK] Файл обновлен")
        
        # Проверяем результат
        print("\n4. ПРОВЕРКА РЕЗУЛЬТАТА:")
        success2, content2, error2 = ssh_exec(ssh, "cat /root/shannon/template/dist/index.html")
        if '/assets/' in content2 and '/app/assets/' not in content2:
            print("  [OK] Пути исправлены правильно!")
            print(f"  Содержимое (первые 500 символов):\n{content2[:500]}")
        else:
            print("  [WARNING] Проверьте содержимое файла")
            print(f"  Содержимое (первые 500 символов):\n{content2[:500]}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()


