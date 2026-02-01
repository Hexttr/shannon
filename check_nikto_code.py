#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка кода Nikto на сервере
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_code():
    """Проверяет код"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 ПРОВЕРКА КОДА NIKTO")
        print("="*60)
        
        # Проверяем метод runNiktoScan
        print("\n1. Метод runNiktoScan:")
        output, _, _ = conn.execute('grep -A 8 "private function runNiktoScan" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php')
        print(output)
        
        # Проверяем метод runNucleiScan
        print("\n2. Метод runNucleiScan:")
        output, _, _ = conn.execute('grep -A 8 "private function runNucleiScan" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php')
        print(output)
        
        # Проверяем метод runDirbScan
        print("\n3. Метод runDirbScan:")
        output, _, _ = conn.execute('grep -A 8 "private function runDirbScan" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php')
        print(output)
        
        # Проверяем последний коммит
        print("\n4. Последний коммит:")
        output, _, _ = conn.execute('cd /root/shannon && git log --oneline -3')
        print(output)
        
        print("\n" + "="*60)
        print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_code()

