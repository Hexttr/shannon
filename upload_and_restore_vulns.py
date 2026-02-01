#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка и выполнение скрипта восстановления уязвимостей
"""

import sys
import os
import base64

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def upload_and_restore():
    """Загружает и выполняет скрипт восстановления"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔧 Восстановление уязвимостей...")
        print("="*60)
        
        # Читаем PHP скрипт
        with open('restore_vulns_simple.php', 'r', encoding='utf-8') as f:
            php_content = f.read()
        
        # Сохраняем на сервере
        print("\n1. Загрузка скрипта на сервер...")
        content_b64 = base64.b64encode(php_content.encode('utf-8')).decode('ascii')
        
        cmd = f'''python3 << 'PYEOF'
import base64
content = base64.b64decode('{content_b64}').decode('utf-8')
with open('/tmp/restore_vulns.php', 'w', encoding='utf-8') as f:
    f.write(content)
PYEOF'''
        conn.execute(cmd)
        conn.execute('cp /tmp/restore_vulns.php /root/shannon/restore_vulns.php')
        print("   ✅ Скрипт загружен")
        
        # Выполняем скрипт
        print("\n2. Выполнение скрипта восстановления...")
        output, error, code = conn.execute('cd /root/shannon && php restore_vulns.php 2>&1')
        print(output)
        if error:
            print(f"Errors: {error}")
        
        # Проверяем результат
        print("\n3. Проверка восстановленных уязвимостей...")
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$pentest = App\\\\Models\\\\Pentest::orderBy('created_at', 'desc')->first();
if (\$pentest) {
    \$vulns = \$pentest->vulnerabilities()->get(['title', 'severity', 'created_at']);
    echo 'Всего уязвимостей: ' . \$vulns->count() . PHP_EOL;
    foreach (\$vulns as \$v) {
        echo '- [' . \$v->severity . '] ' . \$v->title . PHP_EOL;
    }
}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
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
    upload_and_restore()

