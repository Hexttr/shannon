#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка исправления таймаутов SSH
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
        print("📤 Загрузка исправления таймаутов SSH...")
        print("="*60)
        
        # Загружаем SshClientService
        print("\n1. Загрузка SshClientService...")
        with open('backend-laravel/app/Services/SshClientService.php', 'r', encoding='utf-8') as f:
            ssh_content = f.read()
        
        ssh_b64 = base64.b64encode(ssh_content.encode('utf-8')).decode('ascii')
        cmd = f'''python3 << 'PYEOF'
import base64
content = base64.b64decode('{ssh_b64}').decode('utf-8')
with open('/tmp/SshClientService.php', 'w', encoding='utf-8') as f:
    f.write(content)
PYEOF'''
        conn.execute(cmd)
        conn.execute('cp /tmp/SshClientService.php /root/shannon/backend-laravel/app/Services/SshClientService.php')
        print("   ✅ SshClientService обновлен")
        
        # Загружаем PentestEngine
        print("\n2. Загрузка PentestEngine...")
        with open('backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php', 'r', encoding='utf-8') as f:
            engine_content = f.read()
        
        engine_b64 = base64.b64encode(engine_content.encode('utf-8')).decode('ascii')
        cmd = f'''python3 << 'PYEOF'
import base64
content = base64.b64decode('{engine_b64}').decode('utf-8')
with open('/tmp/PentestEngine.php', 'w', encoding='utf-8') as f:
    f.write(content)
PYEOF'''
        conn.execute(cmd)
        conn.execute('cp /tmp/PentestEngine.php /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php')
        print("   ✅ PentestEngine обновлен")
        
        # Проверяем исправления
        print("\n3. Проверка исправлений...")
        output, _, _ = conn.execute('grep -n "setTimeout\|timeout" /root/shannon/backend-laravel/app/Services/SshClientService.php | head -3')
        if output:
            print("   ✅ Таймауты добавлены в SshClientService")
        else:
            print("   ⚠️  Таймауты не найдены")
        
        # Очищаем кэш и перезапускаем queue worker
        print("\n4. Очистка кэша и перезапуск queue worker...")
        conn.execute('cd /root/shannon/backend-laravel && php artisan config:clear && php artisan cache:clear')
        
        # Убиваем зависший job и перезапускаем queue worker
        conn.execute('systemctl restart shannon-queue.service')
        print("   ✅ Кэш очищен, queue worker перезапущен")
        
        print("\n" + "="*60)
        print("✅ Исправления применены!")
        print("="*60)
        print("\n💡 Добавлено:")
        print("   - Таймауты для SSH команд (10-30 минут в зависимости от инструмента)")
        print("   - Команды запускаются через timeout утилиту")
        print("   - SSH соединение имеет таймаут")
        print("\n⚠️  Зависший пентест нужно перезапустить")
        
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

