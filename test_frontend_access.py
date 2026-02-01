#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование доступа к фронтенду
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def test_frontend():
    """Тестирует доступ к фронтенду"""
    print("Тестирование доступа к фронтенду...")
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # Тест загрузки главной страницы
        print("\n[1] Тест загрузки главной страницы:")
        output, error, code = conn.execute("curl -s -o /dev/null -w '%{http_code}' https://72.56.79.153/")
        print(f"HTTP код: {output}")
        
        # Тест загрузки JS файла
        print("\n[2] Тест загрузки JS файла:")
        output, error, code = conn.execute("ls /root/shannon/template/dist/assets/*.js | head -1")
        js_file = output.strip().split('/')[-1] if output.strip() else None
        if js_file:
            print(f"JS файл: {js_file}")
            output, error, code = conn.execute(f"curl -s -o /dev/null -w '%{{http_code}}' https://72.56.79.153/assets/{js_file}")
            print(f"HTTP код: {output}")
        
        # Тест загрузки CSS файла
        print("\n[3] Тест загрузки CSS файла:")
        output, error, code = conn.execute("ls /root/shannon/template/dist/assets/*.css | head -1")
        css_file = output.strip().split('/')[-1] if output.strip() else None
        if css_file:
            print(f"CSS файл: {css_file}")
            output, error, code = conn.execute(f"curl -s -o /dev/null -w '%{{http_code}}' https://72.56.79.153/assets/{css_file}")
            print(f"HTTP код: {output}")
        
        # Тест API
        print("\n[4] Тест API:")
        output, error, code = conn.execute("curl -s -o /dev/null -w '%{http_code}' https://72.56.79.153/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}'")
        print(f"HTTP код: {output}")
        
        # Проверка логов Nginx на ошибки
        print("\n[5] Последние ошибки Nginx (последние 5):")
        output, error, code = conn.execute("tail -5 /var/log/nginx/error.log | grep -v 'rewrite or internal redirection cycle' | tail -5")
        if output.strip():
            print(output)
        else:
            print("Нет критических ошибок")
        
        print("\n[OK] Тестирование завершено!")
        return True

if __name__ == "__main__":
    test_frontend()


