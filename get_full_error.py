#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Получение полной ошибки из логов Laravel
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def get_full_error(conn):
    """Получает полную ошибку из лога"""
    print("\n" + "="*60)
    print("🔍 Получение полной ошибки из лога...")
    print("="*60)
    
    log_file = "/root/shannon/backend-laravel/storage/logs/laravel.log"
    
    # Получаем последние 200 строк и ищем ошибки
    print("\n📋 Последняя ошибка (полный стек):")
    output, error, code = conn.execute(f"tail -n 200 {log_file} 2>&1 | grep -A 100 'ERROR\\|Exception\\|Error' | tail -n 150")
    
    if output:
        print(output)
    else:
        # Если не нашли через grep, просто показываем последние строки
        output, error, code = conn.execute(f"tail -n 100 {log_file} 2>&1")
        if output:
            print(output)

def check_recent_errors(conn):
    """Проверяет недавние ошибки"""
    print("\n" + "="*60)
    print("🔍 Проверка недавних ошибок...")
    print("="*60)
    
    log_file = "/root/shannon/backend-laravel/storage/logs/laravel.log"
    
    # Ищем ошибки за последние 5 минут
    output, error, code = conn.execute(f"grep -i 'error\\|exception\\|fatal' {log_file} | tail -n 20")
    if output:
        print(output)
    else:
        print("   Недавних ошибок не найдено")

def main():
    """Главная функция"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        get_full_error(conn)
        check_recent_errors(conn)
        return True
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()
