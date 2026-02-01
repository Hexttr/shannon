#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка собранного файла на наличие старого URL
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_built_file():
    """Проверяет собранный файл"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 Проверка собранного файла...")
        print("="*60)
        
        # Находим последний файл
        output, _, _ = conn.execute('ls -t /root/shannon/template/dist/assets/index-*.js | head -1')
        latest_file = output.strip()
        
        if not latest_file:
            print("❌ Файл не найден")
            return False
        
        print(f"\nПроверяем файл: {latest_file}")
        
        # Ищем старый URL
        print("\n1. Поиск старого URL (72.56.79.153:8000):")
        output, _, _ = conn.execute(f'grep -o "72.56.79.153:8000" {latest_file} | head -3')
        if output:
            print(f"   Найдено вхождений: {output.count(chr(10)) + 1}")
            # Показываем контекст
            output, _, _ = conn.execute(f'grep -o ".{0,50}72.56.79.153:8000.{0,50}" {latest_file} | head -3')
            print("   Контекст:")
            for line in output.strip().split('\n')[:3]:
                print(f"     ...{line}...")
        else:
            print("   ✅ Старый URL не найден")
        
        # Ищем новый URL
        print("\n2. Поиск нового URL (72.56.79.153/api):")
        output, _, _ = conn.execute(f'grep -o "72.56.79.153/api" {latest_file} | head -3')
        if output:
            print(f"   ✅ Найдено: {output.count(chr(10)) + 1} вхождений")
        else:
            print("   ⚠️  Новый URL не найден")
        
        # Ищем location.protocol
        print("\n3. Поиск location.protocol:")
        output, _, _ = conn.execute(f'grep -o "location.protocol" {latest_file} | head -1')
        if output:
            print("   ✅ Найдено")
        else:
            print("   ⚠️  Не найдено")
        
        # Ищем window.location
        print("\n4. Поиск window.location:")
        output, _, _ = conn.execute(f'grep -o "window.location" {latest_file} | head -1')
        if output:
            print("   ✅ Найдено")
        else:
            print("   ⚠️  Не найдено")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_built_file()

