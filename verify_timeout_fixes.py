#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка применения исправлений таймаутов
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def verify():
    """Проверяет применение исправлений"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 ПРОВЕРКА ИСПРАВЛЕНИЙ ТАЙМАУТОВ")
        print("="*60)
        
        tools = {
            'nmap': ['--max-retries', '--host-timeout'],
            'nikto': ['-timeout', '-useragent'],
            'nuclei': ['-timeout', '-retries', '-rate-limit'],
            'dirb': ['-t', '-H'],
            'sqlmap': ['--timeout', '--retries', '--delay'],
        }
        
        for tool, params in tools.items():
            print(f"\n{tool.upper()}:")
            func_name = f"run{tool.capitalize()}Scan" if tool != 'nmap' else "runNmapScan"
            cmd = f"sed -n '/function {func_name}/,/^    }}/p' /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php"
            output, _, _ = conn.execute(cmd)
            
            found = []
            for param in params:
                if param in output:
                    found.append(param)
            
            if found:
                print(f"   ✅ Найдено: {', '.join(found)}")
            else:
                print(f"   ❌ Параметры не найдены")
                print(f"   Команда: {output[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    verify()

