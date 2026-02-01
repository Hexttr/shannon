#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка кода на сервере и готовности
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def verify_code():
    """Проверяет код на сервере"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 Проверка кода на сервере...")
        print("="*60)
        
        # Проверяем код PentestEngine
        print("\n1. Проверка PentestEngine.php:")
        output, _, _ = conn.execute('grep -A 5 "vulnerabilities()->create" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php')
        print(output)
        
        if "'id' => Str::uuid()->toString()" in output:
            print("\n   ✅ UUID исправление применено")
        else:
            print("\n   ❌ UUID исправление НЕ применено!")
            print("   Применяем исправление...")
            # Загружаем исправленный файл
            with open('backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php', 'r', encoding='utf-8') as f:
                content = f.read()
            import base64
            content_b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
            cmd = f'''python3 << 'PYEOF'
import base64
content = base64.b64decode('{content_b64}').decode('utf-8')
with open('/tmp/PentestEngine.php', 'w', encoding='utf-8') as f:
    f.write(content)
PYEOF'''
            conn.execute(cmd)
            conn.execute('cp /tmp/PentestEngine.php /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php')
            conn.execute('cd /root/shannon/backend-laravel && php artisan config:clear')
            conn.execute('systemctl restart shannon-queue.service')
            print("   ✅ Исправление применено и queue worker перезапущен")
        
        # Проверяем папки с отчетами
        print("\n2. Проверка папок с отчетами:")
        output, _, _ = conn.execute('ls -la /root/shannon/ | grep "pentest.*report" || echo "Папки не найдены"')
        print(output)
        
        # Проверяем как сохраняются результаты
        print("\n3. Как сохраняются результаты:")
        print("   - Данные пентеста: в БД (SQLite)")
        print("   - Уязвимости: в таблице vulnerabilities")
        print("   - Логи: в таблице logs")
        print("   - Временные файлы: в /tmp/ (удаляются автоматически)")
        print("   - Отчеты: НЕ создаются автоматически (только в БД)")
        
        print("\n" + "="*60)
        print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
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
    verify_code()

