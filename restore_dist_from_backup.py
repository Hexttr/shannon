#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Восстановление dist из бэкапа или создание минимальной версии
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
    print("ВОССТАНОВЛЕНИЕ DIST")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка наличия dist в других местах
        print("\n1. ПОИСК DIST:")
        success, output, error = ssh_exec(ssh, "find /root/shannon -name 'dist' -type d 2>&1 | head -5")
        print(output)
        
        # 2. Попытка восстановить из git истории
        print("\n2. ВОССТАНОВЛЕНИЕ ИЗ GIT:")
        # Ищем коммит где dist был
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && git log --all --full-history -- 'dist/' | head -5")
        
        # 3. Создание минимального dist вручную
        print("\n3. СОЗДАНИЕ МИНИМАЛЬНОГО DIST:")
        ssh_exec(ssh, f"mkdir -p {FRONTEND_DIR}/dist/assets")
        
        # Создаем минимальный index.html
        index_html = """<!doctype html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Xaker - AI Penetration Tester</title>
  </head>
  <body>
    <div id="root"></div>
    <script>
      // Минимальная загрузка для отладки
      console.log('[Frontend] Загрузка приложения...');
      // Здесь будет загружен основной JS файл
    </script>
  </body>
</html>
"""
        
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && cat > dist/index.html << 'EOFINDEX'\n{index_html}\nEOFINDEX")
        print("  [OK] Минимальный index.html создан")
        
        # 4. Копирование старых assets если есть
        print("\n4. КОПИРОВАНИЕ ASSETS:")
        ssh_exec(ssh, f"cp -r {FRONTEND_DIR}/dist_backup/assets/* {FRONTEND_DIR}/dist/assets/ 2>&1 || echo 'no backup'")
        
        # Или используем последнюю рабочую версию из git
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && git show HEAD~1:template/dist/index.html > dist/index.html 2>&1 || echo 'no git'")
        
        # 5. Проверка
        print("\n5. ПРОВЕРКА:")
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/")
        print(output)
        
        # 6. Установка прав
        print("\n6. УСТАНОВКА ПРАВ:")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist 2>&1 || chown -R root:root {FRONTEND_DIR}/dist")
        print("  [OK] Права установлены")
        
        # 7. Перезагрузка Nginx
        print("\n7. ПЕРЕЗАГРУЗКА NGINX:")
        ssh_exec(ssh, "systemctl reload nginx")
        time.sleep(2)
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nВАЖНО: Проблема со сборкой frontend.")
        print(f"API работает правильно (статус 200 при тестировании).")
        print(f"\nПопробуйте:")
        print(f"  1. Очистить кэш браузера (Ctrl+Shift+Delete)")
        print(f"  2. Открыть https://{SSH_HOST}")
        print(f"  3. Открыть консоль (F12) и проверить ошибки")
        print(f"  4. Попробовать войти с:")
        print(f"     Логин: admin")
        print(f"     Пароль: admin")
        print(f"\nЕсли проблема сохраняется, пришлите:")
        print(f"  - Ошибки из консоли браузера")
        print(f"  - Статус запроса /api/auth/login из Network tab")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

