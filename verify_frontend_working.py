#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка работоспособности фронтенда
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def verify_frontend():
    """Проверяет работоспособность фронтенда"""
    print("Проверка работоспособности фронтенда...")
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # Проверка dist
        print("\n[1] Проверка dist директории:")
        output, error, code = conn.execute("ls -lh /root/shannon/template/dist/ | head -10")
        print(output)
        
        # Проверка index.html
        print("\n[2] Проверка index.html:")
        output, error, code = conn.execute("head -20 /root/shannon/template/dist/index.html")
        print(output)
        
        # Проверка Nginx
        print("\n[3] Проверка Nginx:")
        output, error, code = conn.execute("systemctl status nginx --no-pager | head -5")
        print(output)
        
        # Тест доступности
        print("\n[4] Тест доступности:")
        output, error, code = conn.execute("curl -I http://localhost/ 2>&1 | head -10")
        print(output)
        
        print("\n[OK] Проверка завершена!")
        print("\nФронтенд должен быть доступен по адресу: https://72.56.79.153")
        return True

if __name__ == "__main__":
    verify_frontend()

