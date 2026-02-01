#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Поиск источника старого URL в собранном файле
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def find_url_source():
    """Ищет источник старого URL"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 Поиск источника старого URL...")
        print("="*60)
        
        # Находим последний файл
        output, _, _ = conn.execute('ls -t /root/shannon/template/dist/assets/index-*.js | head -1')
        latest_file = output.strip()
        
        print(f"\nПроверяем файл: {latest_file}")
        
        # Ищем все вхождения старого URL с контекстом
        print("\n1. Все вхождения старого URL (72.56.79.153:8000):")
        output, _, _ = conn.execute(f'grep -n "72.56.79.153:8000" {latest_file}')
        if output:
            lines = output.strip().split('\n')[:5]
            for line in lines:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    line_num = parts[0]
                    content = parts[1][:100]
                    print(f"   Строка {line_num}: ...{content}...")
        
        # Ищем localhost:8000
        print("\n2. Поиск localhost:8000 (dev URL):")
        output, _, _ = conn.execute(f'grep -n "localhost:8000" {latest_file} | head -3')
        if output:
            print("   Найдено:")
            for line in output.strip().split('\n')[:3]:
                print(f"     {line[:100]}")
        else:
            print("   Не найдено")
        
        # Проверяем исходный файл на сервере
        print("\n3. Проверка исходного api.ts на сервере:")
        output, _, _ = conn.execute('grep -n "72.56.79.153:8000" /root/shannon/template/src/services/api.ts')
        if output:
            print("   ⚠️  Старый URL найден в исходном файле!")
            print(output)
        else:
            print("   ✅ Старый URL не найден в исходном файле")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    find_url_source()

