#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка очереди и Job
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def check_queue():
    """Проверяет очередь и Job"""
    print("Проверка очереди и Job...")
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # Проверка конфигурации очереди
        print("\n[1] Проверка конфигурации очереди:")
        output, error, code = conn.execute("cd /root/shannon/backend-laravel && grep -E 'QUEUE_CONNECTION|QUEUE_DRIVER' .env")
        print(output)
        
        # Проверка что RunPentestJob существует
        print("\n[2] Проверка RunPentestJob:")
        output, error, code = conn.execute("cat /root/shannon/backend-laravel/app/Domain/Pentests/Jobs/RunPentestJob.php | head -50")
        print(output)
        
        # Проверка последних ошибок связанных с Job
        print("\n[3] Последние ошибки связанные с Job:")
        output, error, code = conn.execute("tail -100 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -A 10 'RunPentestJob\\|Job\\|Queue' | tail -30")
        if output.strip():
            print(output)
        else:
            print("Нет ошибок связанных с Job")
        
        # Проверка что очередь работает
        print("\n[4] Проверка статуса очереди:")
        output, error, code = conn.execute("cd /root/shannon/backend-laravel && php artisan queue:work --help 2>&1 | head -5")
        print(output)
        
        return True

if __name__ == "__main__":
    check_queue()

