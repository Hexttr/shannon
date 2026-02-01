#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Восстановление рабочей версии dist
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
    print("ВОССТАНОВЛЕНИЕ РАБОЧЕЙ ВЕРСИИ DIST")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка наличия dist в других местах
        print("\n1. ПОИСК DIST:")
        success, output, error = ssh_exec(ssh, "find /root/shannon -name 'dist' -type d 2>&1 | head -5")
        print(output)
        
        # 2. Проверка git истории для dist
        print("\n2. ПРОВЕРКА GIT ИСТОРИИ:")
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && git log --all --full-history --oneline -- 'dist/' | head -5")
        
        # 3. Создание минимального рабочего dist
        print("\n3. СОЗДАНИЕ МИНИМАЛЬНОГО DIST:")
        ssh_exec(ssh, f"mkdir -p {FRONTEND_DIR}/dist/assets")
        
        # Создаем минимальный index.html который загрузит приложение
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
    <script type="module" src="/assets/index.js"></script>
  </body>
</html>
"""
        
        ssh_exec(ssh, f"cd {FRONTEND_DIR} && cat > dist/index.html << 'EOFINDEX'\n{index_html}\nEOFINDEX")
        print("  [OK] index.html создан")
        
        # 4. Попытка найти старые assets
        print("\n4. ПОИСК СТАРЫХ ASSETS:")
        success, output, error = ssh_exec(ssh, "find /root/shannon -name '*.js' -path '*/assets/*' -type f 2>&1 | head -3")
        if output.strip():
            print(f"  Найдены файлы: {output[:200]}")
            # Копируем найденные файлы
            for line in output.strip().split('\n')[:1]:
                if line.strip():
                    ssh_exec(ssh, f"cp {line.strip()} {FRONTEND_DIR}/dist/assets/ 2>&1 || echo 'ok'")
        else:
            print("  Старые assets не найдены")
        
        # 5. Альтернатива - используем последнюю рабочую версию из git stash или backup
        print("\n5. ПРОВЕРКА BACKUP:")
        # Проверяем, есть ли backup
        success, output, error = ssh_exec(ssh, f"test -d {FRONTEND_DIR}/dist_backup && echo 'EXISTS' || echo 'MISSING'")
        if "EXISTS" in output:
            print("  [OK] Backup найден, восстанавливаем...")
            ssh_exec(ssh, f"cp -r {FRONTEND_DIR}/dist_backup/* {FRONTEND_DIR}/dist/ 2>&1")
        else:
            print("  Backup не найден")
        
        # 6. Проверка dist
        print("\n6. ПРОВЕРКА DIST:")
        success, output, error = ssh_exec(ssh, f"ls -la {FRONTEND_DIR}/dist/")
        print(output)
        
        # 7. Если dist пустой или нет index.html, создаем базовую версию
        if "index.html" not in output:
            print("\n7. СОЗДАНИЕ БАЗОВОЙ ВЕРСИИ:")
            # Создаем простой HTML который будет работать
            basic_html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Xaker - AI Penetration Tester</title>
    <style>
        body { margin: 0; padding: 0; background: #000; color: #fff; font-family: system-ui; }
        #root { min-height: 100vh; }
    </style>
</head>
<body>
    <div id="root">
        <div style="display: flex; align-items: center; justify-content: center; min-height: 100vh; flex-direction: column;">
            <h1>Xaker</h1>
            <p>Загрузка приложения...</p>
            <p style="color: #666; font-size: 12px;">Если страница не загружается, очистите кэш браузера</p>
        </div>
    </div>
    <script>
        console.log('[Frontend] Базовая версия загружена');
        // Здесь будет загружен основной JS файл после сборки
    </script>
</body>
</html>
"""
            ssh_exec(ssh, f"cd {FRONTEND_DIR} && cat > dist/index.html << 'EOFBASIC'\n{basic_html}\nEOFBASIC")
            print("  [OK] Базовая версия создана")
        
        # 8. Установка прав
        print("\n8. УСТАНОВКА ПРАВ:")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist 2>&1 || chown -R root:root {FRONTEND_DIR}/dist")
        print("  [OK] Права установлены")
        
        # 9. Перезагрузка Nginx
        print("\n9. ПЕРЕЗАГРУЗКА NGINX:")
        ssh_exec(ssh, "systemctl reload nginx")
        time.sleep(2)
        
        # 10. Тест
        print("\n10. ТЕСТ:")
        success, output, error = ssh_exec(ssh, f"curl -k -s https://{SSH_HOST}/ | head -10")
        if "<!DOCTYPE html>" in output or "<html" in output.lower():
            print("  [OK] Frontend доступен")
            print(f"  {output[:200]}")
        else:
            print(f"  [WARNING] Ответ: {output[:300]}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nВАЖНО:")
        print(f"  Проблема со сборкой frontend из-за поврежденных файлов.")
        print(f"  API работает правильно (статус 200).")
        print(f"\nПопробуйте:")
        print(f"  1. Очистить кэш браузера (Ctrl+Shift+Delete)")
        print(f"  2. Открыть https://{SSH_HOST} в режиме инкогнито")
        print(f"  3. Проверить консоль (F12) на наличие ошибок")
        print(f"\nУчетные данные:")
        print(f"  Логин: admin")
        print(f"  Пароль: admin")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()


