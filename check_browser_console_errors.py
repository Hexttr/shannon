#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка возможных ошибок в браузере через анализ кода
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def check_for_errors():
    """Проверяет возможные ошибки"""
    print("Проверка возможных ошибок...")
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # Проверка .env файла
        print("\n[1] Проверка .env файла:")
        output, error, code = conn.execute("cat /root/shannon/template/.env")
        print(output)
        
        # Проверка что API URL правильный
        if 'VITE_API_URL' not in output or 'https://72.56.79.153/api' not in output:
            print("\n[2] Исправление .env файла...")
            conn.execute("cd /root/shannon/template && echo 'VITE_API_URL=https://72.56.79.153/api' > .env")
            print("[OK] .env файл обновлен")
        
        # Проверка что dist/index.html правильный
        print("\n[3] Проверка dist/index.html:")
        output, error, code = conn.execute("cat /root/shannon/template/dist/index.html")
        print(output)
        
        # Проверка что assets доступны
        print("\n[4] Проверка доступности assets:")
        output, error, code = conn.execute("ls -la /root/shannon/template/dist/assets/")
        print(output)
        
        # Проверка прав доступа
        print("\n[5] Проверка прав доступа:")
        output, error, code = conn.execute("ls -ld /root/shannon/template/dist /root/shannon/template/dist/index.html /root/shannon/template/dist/assets")
        print(output)
        
        # Тест прямого доступа к файлам
        print("\n[6] Тест прямого доступа к файлам через Nginx:")
        output, error, code = conn.execute("curl -s http://localhost/assets/index-DtRJXMGF-1769932154529.css 2>&1 | head -5")
        if output and '200' in output or 'body' in output.lower():
            print("[OK] CSS файл доступен")
        else:
            print(f"Результат: {output[:200]}")
        
        return True

if __name__ == "__main__":
    check_for_errors()


