#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Прямая проверка логов через SQL
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_logs_direct():
    """Проверяет логи напрямую"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 Прямая проверка логов...")
        print("="*60)
        
        # Проверяем логи через SQL
        print("\n1. Логи через SQL:")
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$pentestId = '75a15a87-23cd-4378-8bc4-d98b413829bb';
\$logs = DB::table('logs')->where('pentest_id', \$pentestId)->orderBy('created_at', 'asc')->get(['id', 'level', 'message', 'created_at']);
echo 'Total logs: ' . \$logs->count() . PHP_EOL;
foreach (\$logs->take(20) as \$log) {
    echo '[' . \$log->level . '] ' . substr(\$log->message, 0, 100) . '... (' . \$log->created_at . ')' . PHP_EOL;
}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        # Проверяем последние логи Laravel
        print("\n2. Последние логи Laravel (pentest related):")
        output, _, _ = conn.execute('tail -100 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -i "pentest\|log\|addlog" | tail -20')
        if output.strip():
            print(output)
        else:
            print("   Нет записей")
        
        # Проверяем логи queue worker
        print("\n3. Последние логи queue worker:")
        output, _, _ = conn.execute('journalctl -u shannon-queue.service --no-pager -n 30 | grep -i "pentest\|log\|error\|exception" | tail -15')
        if output.strip():
            print(output)
        else:
            print("   Нет ошибок")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_logs_direct()

