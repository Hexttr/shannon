#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка ошибки сборки после исправления
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_build_error(conn):
    """Проверяет ошибку сборки"""
    print("\n" + "="*60)
    print("🔍 Проверка ошибки сборки...")
    print("="*60)
    
    template_path = "/root/shannon/template"
    
    # Пробуем собрать и получить полную ошибку
    output, error, code = conn.execute(f"cd {template_path} && npm run build 2>&1 | grep -A 10 'ERROR\\|error' | head -30")
    
    if output:
        print("Ошибка сборки:")
        print(output)
    else:
        # Пробуем получить полный вывод
        output2, error2, code2 = conn.execute(f"cd {template_path} && npm run build 2>&1 | tail -n 50")
        if output2:
            print("Последние строки вывода:")
            print(output2)

def check_file_on_server(conn):
    """Проверяет файл на сервере"""
    print("\n" + "="*60)
    print("🔍 Проверка файла на сервере...")
    print("="*60)
    
    file_path = "/root/shannon/template/src/pages/Reports.tsx"
    
    # Проверяем первые строки
    output, error, code = conn.execute(f"head -n 70 {file_path} | tail -n 15")
    if output:
        print("Строки 55-70:")
        print(output)
    
    # Проверяем строку 63
    output2, error2, code2 = conn.execute(f"sed -n '63p' {file_path}")
    if output2:
        print(f"\nСтрока 63:")
        print(output2)

def main():
    """Главная функция"""
    print("="*60)
    print("🔍 Проверка ошибки сборки")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        check_file_on_server(conn)
        check_build_error(conn)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


