#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка фронтенда и исправление конфигурации Nginx
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def rebuild_frontend_and_fix():
    """Собирает фронтенд и исправляет Nginx"""
    print("Сборка фронтенда и исправление конфигурации...")
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # 1. Проверка Node.js и npm
        print("\n[1] Проверка Node.js и npm:")
        output, error, code = conn.execute("node --version && npm --version")
        print(output)
        
        # 2. Переход в директорию template
        print("\n[2] Переход в директорию template...")
        conn.execute("cd /root/shannon/template && pwd")
        
        # 3. Проверка .env файла
        print("\n[3] Проверка .env файла:")
        output, error, code = conn.execute("cd /root/shannon/template && cat .env 2>/dev/null || echo 'Файл .env не найден'")
        print(output)
        
        # 4. Создание/обновление .env файла
        print("\n[4] Создание .env файла...")
        env_content = """VITE_API_URL=https://72.56.79.153/api
"""
        conn.execute(f"cd /root/shannon/template && cat > .env << 'ENV_EOF'\n{env_content}ENV_EOF")
        
        # 5. Установка зависимостей (если нужно)
        print("\n[5] Проверка node_modules...")
        output, error, code = conn.execute("cd /root/shannon/template && test -d node_modules && echo 'OK' || echo 'Нужна установка'")
        print(output)
        
        if 'Нужна установка' in output:
            print("\n[6] Установка зависимостей npm...")
            output, error, code = conn.execute("cd /root/shannon/template && npm install 2>&1")
            print(output[:500] if output else "Установка завершена")
        
        # 6. Сборка фронтенда
        print("\n[7] Сборка фронтенда...")
        output, error, code = conn.execute("cd /root/shannon/template && npm run build 2>&1")
        print(output[-1000:] if output else "Сборка завершена")
        if error:
            print(f"Ошибки: {error[-500:]}")
        
        # 7. Проверка результата сборки
        print("\n[8] Проверка результата сборки:")
        output, error, code = conn.execute("ls -la /root/shannon/template/dist/ | head -10")
        print(output)
        
        # 8. Исправление конфигурации Nginx
        print("\n[9] Исправление конфигурации Nginx...")
        
        # Читаем текущую конфигурацию полностью
        output, error, code = conn.execute("cat /etc/nginx/sites-available/shannon")
        current_config = output
        
        # Заменяем проблемную строку try_files
        fixed_config = current_config.replace(
            '    location / {\n        try_files $uri $uri/ /index.html;\n    }',
            '''    location / {
        try_files $uri $uri/ @fallback;
    }
    
    location @fallback {
        rewrite ^.*$ /index.html last;
    }'''
        )
        
        # Сохраняем исправленную конфигурацию
        conn.execute(f"cat > /tmp/shannon_nginx_fixed.conf << 'NGINX_EOF'\n{fixed_config}\nNGINX_EOF")
        
        # Проверяем синтаксис
        print("\n[10] Проверка синтаксиса Nginx:")
        output, error, code = conn.execute("nginx -t 2>&1")
        print(output)
        
        if code == 0:
            # Применяем конфигурацию
            print("\n[11] Применение конфигурации...")
            conn.execute("cp /tmp/shannon_nginx_fixed.conf /etc/nginx/sites-available/shannon")
            output, error, code = conn.execute("nginx -t && systemctl reload nginx 2>&1")
            print(output)
            
            print("\n[OK] Фронтенд собран и конфигурация Nginx исправлена!")
            return True
        else:
            print("\n[ERROR] Ошибка в конфигурации Nginx!")
            return False

if __name__ == "__main__":
    success = rebuild_frontend_and_fix()
    sys.exit(0 if success else 1)


