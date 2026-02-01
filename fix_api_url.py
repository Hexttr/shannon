#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление API URL для использования HTTPS
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
    print("="*70)
    print("ИСПРАВЛЕНИЕ API URL ДЛЯ HTTPS")
    print("="*70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Читаем текущий api.ts
        print("\n1. ЧТЕНИЕ API.TS:")
        success, content, error = ssh_exec(ssh, f"cat {FRONTEND_DIR}/src/services/api.ts")
        if not success:
            print(f"  [ERROR] Не удалось прочитать файл: {error}")
            return
        
        print(f"  [OK] Файл прочитан ({len(content)} байт)")
        
        # Заменяем определение API_URL
        print("\n2. ИСПРАВЛЕНИЕ API URL:")
        new_api_url_code = '''import axios from 'axios';

// Автоматически определяем API URL на основе текущего протокола
const getApiUrl = () => {
  // Если указана переменная окружения - используем её
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // В production используем тот же протокол и хост, что и текущая страница
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return `${window.location.protocol}//${window.location.host}/api`;
  }
  
  // В development используем localhost
  return 'http://localhost:8000/api';
};

const API_URL = getApiUrl();'''
        
        # Заменяем старую строку на новую
        import re
        old_pattern = r"const API_URL = import\.meta\.env\.VITE_API_URL \|\| 'http://localhost:8000/api';"
        new_content = re.sub(old_pattern, new_api_url_code, content)
        
        if new_content == content:
            # Пробуем другой паттерн
            old_pattern2 = r"const API_URL = .*?;"
            new_content = re.sub(old_pattern2, new_api_url_code, content, flags=re.DOTALL)
        
        if new_content != content:
            # Записываем обратно
            ssh_exec(ssh, f"cat > {FRONTEND_DIR}/src/services/api.ts << 'API_EOF'\n{new_content}\nAPI_EOF")
            print("  [OK] API URL исправлен")
        else:
            print("  [WARNING] Не удалось найти паттерн для замены")
            # Записываем полностью новый файл
            new_file_content = new_api_url_code + content.split('const api = axios.create')[1]
            ssh_exec(ssh, f"cat > {FRONTEND_DIR}/src/services/api.ts << 'API_EOF'\n{new_file_content}\nAPI_EOF")
            print("  [OK] Файл перезаписан")
        
        # Проверяем результат
        print("\n3. ПРОВЕРКА РЕЗУЛЬТАТА:")
        success2, content2, error2 = ssh_exec(ssh, f"grep -A 5 'getApiUrl' {FRONTEND_DIR}/src/services/api.ts | head -10")
        if 'getApiUrl' in content2:
            print("  [OK] Функция getApiUrl найдена")
            print(f"  {content2}")
        else:
            print("  [WARNING] Функция getApiUrl не найдена")
        
        # Пересобираем фронтенд
        print("\n4. ПЕРЕСБОРКА ФРОНТЕНДА:")
        print("  Это может занять 2-3 минуты...")
        
        # Удаляем старый dist
        ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/dist")
        
        # Запускаем сборку
        stdin, stdout, stderr = ssh.exec_command(f"cd {FRONTEND_DIR} && npm run build 2>&1")
        output_lines = []
        while True:
            line = stdout.readline()
            if not line:
                break
            output_lines.append(line)
            if len(output_lines) % 20 == 0:
                print(f"  Собрано строк: {len(output_lines)}...")
        
        exit_status = stdout.channel.recv_exit_status()
        output = ''.join(output_lines)
        
        if exit_status == 0:
            print("  [OK] Сборка завершена")
        else:
            print(f"  [ERROR] Ошибка сборки:")
            print(output[-500:])
            return
        
        # Исправляем пути в index.html
        print("\n5. ИСПРАВЛЕНИЕ ПУТЕЙ В INDEX.HTML:")
        success3, html_content, error3 = ssh_exec(ssh, f"cat {FRONTEND_DIR}/dist/index.html")
        if '/app/assets/' in html_content:
            fixed_html = html_content.replace('/app/assets/', '/assets/')
            ssh_exec(ssh, f"cat > {FRONTEND_DIR}/dist/index.html << 'HTML_EOF'\n{fixed_html}\nHTML_EOF")
            print("  [OK] Пути исправлены")
        else:
            print("  [OK] Пути уже правильные")
        
        # Устанавливаем права доступа
        print("\n6. УСТАНОВКА ПРАВ ДОСТУПА:")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        print("  [OK] Права установлены")
        
        print("\n" + "="*70)
        print("ГОТОВО!")
        print("="*70)
        print("\nТеперь API запросы будут идти через HTTPS.")
        print("Обновите страницу в браузере (Ctrl+F5) и попробуйте войти снова.")
        print("="*70)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()



