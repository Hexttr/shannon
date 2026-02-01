#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка UUID исправления на сервере
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def verify_uuid():
    """Проверяет UUID исправление"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 Проверка UUID исправления...")
        print("="*60)
        
        # Читаем файл напрямую
        print("\n1. Проверка кода создания уязвимостей:")
        output, _, _ = conn.execute('sed -n "/vulnerabilities()->create/,/});/p" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php | head -10')
        print(output)
        
        if "'id' => Str::uuid()->toString()" in output or '"id" => Str::uuid()->toString()' in output:
            print("\n   ✅ UUID исправление ПРИМЕНЕНО!")
        else:
            print("\n   ❌ UUID исправление НЕ найдено!")
            print("   Применяем исправление...")
            
            # Читаем локальный файл
            with open('backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Загружаем на сервер
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
        
        # Проверяем еще раз
        print("\n2. Повторная проверка:")
        output, _, _ = conn.execute('sed -n "/vulnerabilities()->create/,/});/p" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php | head -10')
        if "'id' => Str::uuid()->toString()" in output or '"id" => Str::uuid()->toString()' in output:
            print("   ✅ UUID исправление подтверждено!")
        else:
            print("   ⚠️  UUID все еще не найден")
            print(output)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    verify_uuid()

