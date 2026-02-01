#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка ошибок фронтенда
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def check_frontend_errors():
    """Проверяет ошибки фронтенда"""
    print("Проверка ошибок фронтенда...")
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # Проверка index.html
        print("\n[1] Проверка index.html:")
        output, error, code = conn.execute("cat /root/shannon/template/dist/index.html")
        print(output)
        
        # Проверка путей в index.html
        print("\n[2] Проверка путей к assets:")
        if '/app/assets/' in output:
            print("[WARNING] Обнаружены пути /app/assets/ - возможно неправильный base path")
        
        # Проверка существования assets
        print("\n[3] Проверка существования assets:")
        output, error, code = conn.execute("ls -la /root/shannon/template/dist/assets/ | head -10")
        print(output)
        
        # Проверка Nginx конфигурации
        print("\n[4] Проверка конфигурации Nginx:")
        output, error, code = conn.execute("cat /etc/nginx/sites-available/shannon")
        print(output)
        
        # Проверка логов Nginx
        print("\n[5] Последние ошибки Nginx:")
        output, error, code = conn.execute("tail -20 /var/log/nginx/error.log")
        print(output)
        
        # Тест загрузки index.html
        print("\n[6] Тест загрузки index.html через curl:")
        output, error, code = conn.execute("curl -s https://72.56.79.153/ | head -20")
        print(output)
        
        # Тест загрузки JS файла
        print("\n[7] Тест загрузки JS файла:")
        js_file = None
        if '/app/assets/' in output:
            # Извлекаем имя JS файла
            import re
            match = re.search(r'/app/assets/([^"]+\.js)', output)
            if match:
                js_file = match.group(1)
                print(f"Найден JS файл: {js_file}")
                output, error, code = conn.execute(f"curl -I https://72.56.79.153/app/assets/{js_file} 2>&1 | head -10")
                print(output)
        
        return True

if __name__ == "__main__":
    check_frontend_errors()

