#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка исправления frontend
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def verify_fix():
    """Проверяет что исправление применено"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 Проверка исправления frontend...")
        print("="*60)
        
        # Проверяем исходный файл
        print("\n1. Проверка api.ts на сервере:")
        output, _, _ = conn.execute('grep -A 15 "getApiUrl" /root/shannon/template/src/services/api.ts')
        print(output)
        
        # Проверяем что используется window.location.protocol
        print("\n2. Проверка использования window.location.protocol:")
        output, _, _ = conn.execute('grep "window.location.protocol" /root/shannon/template/src/services/api.ts')
        if output:
            print("   ✅ Используется window.location.protocol")
        else:
            print("   ❌ window.location.protocol не найден")
        
        # Проверяем собранный файл
        print("\n3. Проверка собранного файла:")
        output, _, _ = conn.execute('ls -lh /root/shannon/template/dist/assets/index-*.js | tail -1')
        latest_file = output.split()[-1] if output else None
        if latest_file:
            print(f"   Последний файл: {latest_file}")
            # Проверяем что в собранном файле есть правильная логика
            output, _, _ = conn.execute(f'grep -o "location.protocol" {latest_file} | head -1')
            if output:
                print("   ✅ В собранном файле используется location.protocol")
            else:
                print("   ⚠️  location.protocol не найден в собранном файле")
        
        print("\n" + "="*60)
        print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
        print("="*60)
        print("\n💡 Инструкции:")
        print("   1. Обновите страницу в браузере (Ctrl+F5 или Cmd+Shift+R)")
        print("   2. Очистите кэш браузера если нужно")
        print("   3. Проверьте консоль браузера - должно быть:")
        print("      - API URL должен быть: https://72.56.79.153/api")
        print("      - Не должно быть ошибок Mixed Content")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    verify_fix()

