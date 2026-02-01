#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест выполнения SSH команд
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def test_commands():
    """Тестирует выполнение команд"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🧪 ТЕСТ ВЫПОЛНЕНИЯ SSH КОМАНД")
        print("="*60)
        
        # 1. Тест простой команды
        print("\n1. Тест простой команды:")
        output, _, code = conn.execute('echo "test"')
        print(f"   Результат: {output.strip()}, Exit code: {code}")
        
        # 2. Тест команды с переменной окружения
        print("\n2. Тест команды с переменной окружения:")
        output, _, code = conn.execute("HTTP_USER_AGENT='Mozilla/5.0' echo test")
        print(f"   Результат: {output.strip()}, Exit code: {code}")
        
        # 3. Тест команды nmap
        print("\n3. Тест команды nmap:")
        output, _, code = conn.execute("timeout 5 nmap --version 2>&1")
        print(f"   Результат: {output[:200]}, Exit code: {code}")
        
        # 4. Тест команды nikto с переменной окружения
        print("\n4. Тест команды nikto:")
        output, _, code = conn.execute("HTTP_USER_AGENT='Mozilla/5.0' timeout 5 nikto -Version 2>&1")
        print(f"   Результат: {output[:200]}, Exit code: {code}")
        
        # 5. Тест команды через bash -c
        print("\n5. Тест команды через bash -c:")
        output, _, code = conn.execute("bash -c 'HTTP_USER_AGENT=\"Mozilla/5.0\" echo test'")
        print(f"   Результат: {output.strip()}, Exit code: {code}")
        
        print("\n" + "="*60)
        print("✅ ТЕСТ ЗАВЕРШЕН")
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
    test_commands()

