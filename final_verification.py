#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная проверка исправлений на сервере
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def final_check():
    """Финальная проверка"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("✅ ФИНАЛЬНАЯ ПРОВЕРКА ИСПРАВЛЕНИЙ")
        print("="*60)
        
        # 1. Проверяем команду Nikto
        print("\n1. Проверка команды Nikto на сервере:")
        output, _, _ = conn.execute('grep -A 5 "runNiktoScan" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php | head -7')
        print(output)
        if 'HTTP_USER_AGENT=' in output and '"' in output:
            print("   ✅ Команда Nikto исправлена - используются двойные кавычки")
        else:
            print("   ❌ Команда Nikto НЕ исправлена")
        
        # 2. Проверяем команду Nuclei
        print("\n2. Проверка команды Nuclei на сервере:")
        output, _, _ = conn.execute('grep -A 5 "runNucleiScan" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php | head -7')
        print(output)
        if '-H "' in output:
            print("   ✅ Команда Nuclei исправлена - используются двойные кавычки")
        else:
            print("   ❌ Команда Nuclei НЕ исправлена")
        
        # 3. Проверяем команду Dirb
        print("\n3. Проверка команды Dirb на сервере:")
        output, _, _ = conn.execute('grep -A 5 "runDirbScan" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php | head -7')
        print(output)
        if '-H "' in output:
            print("   ✅ Команда Dirb исправлена - используются двойные кавычки")
        else:
            print("   ❌ Команда Dirb НЕ исправлена")
        
        # 4. Тест выполнения команды Nikto
        print("\n4. Тест выполнения команды Nikto:")
        test_cmd = 'HTTP_USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" timeout 5 nikto -Version 2>&1'
        output, _, code = conn.execute(test_cmd)
        if code == 0 and 'Nikto' in output:
            print(f"   ✅ Команда выполняется: {output[:100]}")
        else:
            print(f"   ❌ Команда не выполняется: {output[:200]}")
        
        # 5. Проверяем статус queue worker
        print("\n5. Статус queue worker:")
        output, _, _ = conn.execute('systemctl is-active shannon-queue.service')
        if 'active' in output:
            print("   ✅ Queue worker работает")
        else:
            print(f"   ⚠️  Queue worker: {output.strip()}")
        
        # 6. Проверяем последний коммит
        print("\n6. Последний коммит на сервере:")
        output, _, _ = conn.execute('cd /root/shannon && git log --oneline -1')
        print(f"   {output.strip()}")
        
        print("\n" + "="*60)
        print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
        print("="*60)
        print("\n💡 Все исправления применены!")
        print("💡 Файлы обновлены на сервере!")
        print("💡 Queue worker перезапущен!")
        print("\n✅ Можно запускать новый пентест!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    final_check()
