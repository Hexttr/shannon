#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Получение полного стека ошибки
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def get_full_error():
    """Получает полный стек ошибки"""
    print("Получение полного стека ошибки...")
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # Получаем последнюю ошибку полностью
        print("\n[1] Последняя ошибка (полный стек):")
        output, error, code = conn.execute("tail -200 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -B 5 -A 50 'production.ERROR' | tail -60")
        print(output)
        
        # Ищем конкретную ошибку связанную с PentestEngine
        print("\n[2] Ошибки связанные с PentestEngine:")
        output, error, code = conn.execute("tail -200 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -B 5 -A 20 'PentestEngine' | tail -30")
        if output.strip():
            print(output)
        else:
            print("Нет ошибок связанных с PentestEngine")
        
        # Проверка существования PentestEngine
        print("\n[3] Проверка PentestEngine:")
        output, error, code = conn.execute("test -f /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php && echo 'EXISTS' || echo 'NOT_FOUND'")
        print(output)
        if 'EXISTS' in output:
            output, error, code = conn.execute("cat /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php | head -50")
            print(output)
        
        return True

if __name__ == "__main__":
    get_full_error()

