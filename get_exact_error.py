#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Получение точной ошибки
"""

import sys
import os
import time

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def get_exact_error(conn):
    """Получает точную ошибку"""
    print("\n" + "="*60)
    print("🔍 Получение точной ошибки...")
    print("="*60)
    
    log_file = "/root/shannon/backend-laravel/storage/logs/laravel.log"
    
    # Очищаем лог
    conn.execute(f"echo '' > {log_file}")
    
    # Делаем запрос
    print("\n📡 Отправка запроса...")
    conn.execute("curl -s http://localhost:8000/api/pentests > /dev/null 2>&1")
    
    time.sleep(1)
    
    # Читаем ошибку
    output, error, code = conn.execute(f"cat {log_file} 2>&1")
    if output:
        # Ищем первую ошибку
        lines = output.split('\n')
        error_start = None
        for i, line in enumerate(lines):
            if 'ERROR' in line or 'Exception' in line:
                error_start = i
                break
        
        if error_start is not None:
            # Показываем ошибку и стек трейс
            error_lines = lines[error_start:error_start+80]
            print("\n".join(error_lines))
        else:
            print("Полный лог:")
            print(output[:2000])

def main():
    """Главная функция"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        get_exact_error(conn)
        return True
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


