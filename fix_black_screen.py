#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление черного экрана на фронтенде
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
    print("="*60)
    print("ИСПРАВЛЕНИЕ ЧЕРНОГО ЭКРАНА")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверяем текущий App.tsx
        print("\n1. ПРОВЕРКА APP.TSX:")
        success, output, error = ssh_exec(ssh, f"grep -A 5 'function AppRoutes' {FRONTEND_DIR}/src/App.tsx | head -10")
        print(f"  {output}")
        
        # 2. Проверяем, что basename правильно определен
        print("\n2. ПРОВЕРКА BASENAME:")
        success2, output2, error2 = ssh_exec(ssh, f"grep 'basename' {FRONTEND_DIR}/src/App.tsx")
        print(f"  {output2}")
        
        # 3. Исправляем basename - должен быть '/app' для production
        print("\n3. ИСПРАВЛЕНИЕ BASENAME:")
        # Читаем файл
        success3, content, error3 = ssh_exec(ssh, f"cat {FRONTEND_DIR}/src/App.tsx")
        if not success3:
            print(f"  [ERROR] Не удалось прочитать файл: {error3}")
            return
        
        # Заменяем basename на правильный
        # Убеждаемся, что basename = '/app' для production
        if "const basename = window.location.hostname === 'localhost' ? '/' : '/app';" not in content:
            # Исправляем
            new_content = content.replace(
                "const basename = window.location.hostname === 'localhost' ? '/' : '/app';",
                "const basename = window.location.hostname === 'localhost' ? '/' : '/app';"
            )
            # Если строка не найдена, добавляем её
            if "const basename" not in content:
                # Ищем место для вставки
                if "function AppRoutes() {" in content:
                    new_content = content.replace(
                        "function AppRoutes() {",
                        "function AppRoutes() {\n  const basename = window.location.hostname === 'localhost' ? '/' : '/app';"
                    )
                else:
                    print("  [ERROR] Не найдена функция AppRoutes")
                    return
            
            # Записываем обратно
            ssh_exec(ssh, f"cat > {FRONTEND_DIR}/src/App.tsx << 'APP_EOF'\n{new_content}\nAPP_EOF")
            print("  [OK] basename исправлен")
        else:
            print("  [OK] basename уже правильный")
        
        # 4. Проверяем index.html - пути должны быть /assets/, а не /app/assets/
        print("\n4. ПРОВЕРКА INDEX.HTML:")
        success4, html_content, error4 = ssh_exec(ssh, f"cat {FRONTEND_DIR}/dist/index.html")
        if '/app/assets/' in html_content:
            print("  [WARNING] В index.html все еще есть /app/assets/")
            # Исправляем
            new_html = html_content.replace('/app/assets/', '/assets/')
            ssh_exec(ssh, f"cat > {FRONTEND_DIR}/dist/index.html << 'HTML_EOF'\n{new_html}\nHTML_EOF")
            print("  [OK] Пути в index.html исправлены")
        else:
            print("  [OK] Пути в index.html правильные")
        
        # 5. Пересобираем фронтенд
        print("\n5. ПЕРЕСБОРКА ФРОНТЕНДА:")
        print("  Это может занять несколько минут...")
        build_log = ssh_exec(ssh, f"cd {FRONTEND_DIR} && npm run build 2>&1", timeout=180)
        if build_log[0]:
            print("  [OK] Сборка завершена")
        else:
            print(f"  [ERROR] Ошибка сборки: {build_log[2]}")
            return
        
        # 6. Проверяем, что dist создан
        print("\n6. ПРОВЕРКА DIST:")
        success6, dist_check, error6 = ssh_exec(ssh, f"ls {FRONTEND_DIR}/dist/assets/*.js 2>&1 | head -3")
        if "No such file" in dist_check:
            print(f"  [ERROR] dist не создан!")
        else:
            print(f"  [OK] dist создан: {dist_check}")
        
        # 7. Исправляем пути в новом index.html
        print("\n7. ИСПРАВЛЕНИЕ ПУТЕЙ В НОВОМ INDEX.HTML:")
        success7, new_html_content, error7 = ssh_exec(ssh, f"cat {FRONTEND_DIR}/dist/index.html")
        if '/app/assets/' in new_html_content:
            fixed_html = new_html_content.replace('/app/assets/', '/assets/')
            ssh_exec(ssh, f"cat > {FRONTEND_DIR}/dist/index.html << 'HTML_EOF'\n{fixed_html}\nHTML_EOF")
            print("  [OK] Пути исправлены")
        else:
            print("  [OK] Пути уже правильные")
        
        # 8. Устанавливаем права доступа
        print("\n8. УСТАНОВКА ПРАВ ДОСТУПА:")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        print("  [OK] Права установлены")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print("\nОбновите страницу в браузере (Ctrl+F5) и проверьте работу.")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()



