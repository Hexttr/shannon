#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест выполнения команд через SSH
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
        print("🧪 ТЕСТ ВЫПОЛНЕНИЯ КОМАНД ЧЕРЕЗ BASH -C")
        print("="*60)
        
        # Тест 1: Простая команда
        print("\n1. Простая команда:")
        output, _, code = conn.execute('echo "test"')
        print(f"   Результат: {output.strip()}, Exit code: {code}")
        
        # Тест 2: Команда с переменной окружения
        print("\n2. Команда с переменной окружения (как Nikto):")
        cmd = 'HTTP_USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" echo test'
        output, _, code = conn.execute(cmd)
        print(f"   Команда: {cmd}")
        print(f"   Результат: {output.strip()}, Exit code: {code}")
        
        # Тест 3: Команда nmap
        print("\n3. Команда nmap:")
        cmd = 'nmap --version'
        output, _, code = conn.execute(cmd)
        print(f"   Результат: {output[:100]}, Exit code: {code}")
        
        # Тест 4: Команда nikto с переменной окружения
        print("\n4. Команда nikto с переменной окружения:")
        cmd = 'HTTP_USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" timeout 5 nikto -Version'
        output, _, code = conn.execute(cmd)
        print(f"   Результат: {output[:150]}, Exit code: {code}")
        
        # Тест 5: Команда через bash -c напрямую (как будет выполняться)
        print("\n5. Команда через bash -c (как в SSH клиенте):")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        escaped_cmd = f'HTTP_USER_AGENT="{user_agent}" echo test'
        escaped_cmd = escaped_cmd.replace("'", "'\\''")
        bash_cmd = f"bash -c '{escaped_cmd}'"
        output, _, code = conn.execute(bash_cmd)
        print(f"   Команда: {bash_cmd}")
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

