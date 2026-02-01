#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка почему пентест не запускается
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check():
    """Проверяет почему не запускается"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 ПРОВЕРКА ПОЧЕМУ ПЕНТЕСТ НЕ ЗАПУСКАЕТСЯ")
        print("="*60)
        
        # 1. Проверяем есть ли pending пентесты
        print("\n1. Пентесты со статусом pending:")
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$pentests = App\\\\Models\\\\Pentest::where('status', 'pending')->orderBy('created_at', 'desc')->get(['id', 'target_url', 'created_at']);
echo 'Pending пентестов: ' . \$pentests->count() . PHP_EOL;
foreach (\$pentests as \$p) {
    echo 'ID: ' . \$p->id . ', Target: ' . \$p->target_url . ', Created: ' . \$p->created_at . PHP_EOL;
}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        # 2. Проверяем последние ошибки
        print("\n2. Последние ошибки в логах:")
        output, _, _ = conn.execute('tail -50 /root/shannon/backend-laravel/storage/logs/laravel.log | tail -20')
        print(output)
        
        # 3. Проверяем что происходит при запуске
        print("\n3. Тест запуска pending пентеста:")
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$pentest = App\\\\Models\\\\Pentest::where('status', 'pending')->orderBy('created_at', 'desc')->first();
if (\$pentest) {
    echo 'Найден pending пентест: ' . \$pentest->id . PHP_EOL;
    try {
        \$action = new App\\\\Domain\\\\Pentests\\\\Actions\\\\StartPentestAction();
        \$action->execute(\$pentest->id);
        echo 'Запуск выполнен успешно' . PHP_EOL;
        
        \$jobs = DB::table('jobs')->count();
        echo 'Jobs в очереди: ' . \$jobs . PHP_EOL;
    } catch (Exception \$e) {
        echo 'Ошибка запуска: ' . \$e->getMessage() . PHP_EOL;
        echo 'Trace: ' . \$e->getTraceAsString() . PHP_EOL;
    }
} else {
    echo 'Нет pending пентестов' . PHP_EOL;
}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        # 4. Проверяем queue worker обрабатывает ли jobs
        print("\n4. Проверка обработки jobs queue worker:")
        output, _, _ = conn.execute('sleep 3 && journalctl -u shannon-queue.service --no-pager -n 30 | tail -15')
        print(output)
        
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
    check()

