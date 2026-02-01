#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление queue worker и проверка логов
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def fix_queue():
    """Исправляет queue worker"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔧 Исправление queue worker...")
        print("="*60)
        
        # 1. Проверяем статус
        print("\n1. Статус queue worker:")
        output, _, _ = conn.execute('systemctl status shannon-queue.service --no-pager | head -10')
        print(output)
        
        # 2. Перезапускаем queue worker
        print("\n2. Перезапуск queue worker...")
        conn.execute('systemctl restart shannon-queue.service')
        output, _, _ = conn.execute('sleep 2 && systemctl status shannon-queue.service --no-pager | head -10')
        print(output)
        
        # 3. Проверяем job в очереди
        print("\n3. Проверка job в очереди:")
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$job = DB::table('jobs')->first();
if (\$job) {
    echo 'Job exists, attempts: ' . \$job->attempts . PHP_EOL;
    echo 'Job payload: ' . substr(\$job->payload, 0, 200) . PHP_EOL;
} else {
    echo 'No jobs in queue' . PHP_EOL;
}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        # 4. Ждем немного и проверяем логи
        print("\n4. Ожидание обработки job (10 секунд)...")
        import time
        time.sleep(10)
        
        # 5. Проверяем логи пентеста
        print("\n5. Проверка логов пентеста:")
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$pentest = App\\\\Models\\\\Pentest::orderBy('created_at', 'desc')->first();
if (\$pentest) {
    \$logs = \$pentest->logs()->orderBy('created_at', 'asc')->get(['level', 'message', 'created_at']);
    echo 'Logs count: ' . \$logs->count() . PHP_EOL;
    foreach (\$logs->take(10) as \$log) {
        echo '[' . \$log->level . '] ' . substr(\$log->message, 0, 80) . PHP_EOL;
    }
}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        # 6. Проверяем статус пентеста
        print("\n6. Статус пентеста:")
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$pentest = App\\\\Models\\\\Pentest::orderBy('created_at', 'desc')->first();
if (\$pentest) {
    echo 'Status: ' . \$pentest->status . PHP_EOL;
    echo 'Started: ' . \$pentest->started_at . PHP_EOL;
    echo 'Updated: ' . \$pentest->updated_at . PHP_EOL;
}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        print("\n" + "="*60)
        print("✅ Проверка завершена")
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
    fix_queue()

