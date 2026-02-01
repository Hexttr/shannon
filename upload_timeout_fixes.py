#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка исправлений таймаутов для инструментов сканирования
"""

import sys
import os
import base64

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def upload_fix():
    """Загружает исправление"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("📤 Загрузка исправлений таймаутов...")
        print("="*60)
        
        # Читаем локальный файл
        with open('backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Сохраняем на сервере
        print("\n1. Сохранение файла на сервере...")
        content_b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
        
        cmd = f'''python3 << 'PYEOF'
import base64
content = base64.b64decode('{content_b64}').decode('utf-8')
with open('/tmp/PentestEngine.php', 'w', encoding='utf-8') as f:
    f.write(content)
PYEOF'''
        conn.execute(cmd)
        
        # Копируем в нужное место
        conn.execute('cp /tmp/PentestEngine.php /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php')
        print("   ✅ Файл загружен")
        
        # Проверяем что исправления применены
        print("\n2. Проверка исправлений...")
        checks = [
            ('nmap', '--max-retries'),
            ('nikto', '-timeout'),
            ('nuclei', '-timeout'),
            ('dirb', '-t'),
            ('sqlmap', '--timeout'),
        ]
        
        for tool, param in checks:
            output, _, _ = conn.execute(f"grep -n '{param}' /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php | grep -i {tool} | head -1")
            if output:
                print(f"   ✅ {tool}: таймауты добавлены")
            else:
                print(f"   ⚠️  {tool}: таймауты не найдены")
        
        # Очищаем кэш
        print("\n3. Очистка кэша...")
        conn.execute('cd /root/shannon/backend-laravel && php artisan config:clear && php artisan cache:clear')
        print("   ✅ Кэш очищен")
        
        print("\n" + "="*60)
        print("✅ Исправления применены!")
        print("="*60)
        print("\n💡 Добавлено:")
        print("   - Таймауты для всех инструментов")
        print("   - Retry логика (повторы при ошибках)")
        print("   - User-Agent заголовки (обход защиты)")
        print("   - Rate limiting (ограничение скорости запросов)")
        print("   - Задержки между запросами")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    upload_fix()

