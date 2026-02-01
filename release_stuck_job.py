#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Освобождение зависшего job
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def release_job():
    """Освобождает зависший job"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔧 ОСВОБОЖДЕНИЕ ЗАВИСШЕГО JOB")
        print("="*60)
        
        # Освобождаем все зарезервированные jobs
        print("\n1. Освобождение зарезервированных jobs...")
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$before = DB::table('jobs')->whereNotNull('reserved_at')->count();
echo 'Зарезервированных jobs до: ' . \$before . PHP_EOL;

// Освобождаем все зарезервированные jobs
DB::table('jobs')->whereNotNull('reserved_at')->update([
    'reserved_at' => null,
    'attempts' => DB::raw('attempts + 1')
]);

\$after = DB::table('jobs')->whereNotNull('reserved_at')->count();
echo 'Зарезервированных jobs после: ' . \$after . PHP_EOL;
echo 'Jobs освобождены' . PHP_EOL;
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        # Проверяем статус
        print("\n2. Статус после освобождения:")
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$jobs = DB::table('jobs')->get(['id', 'queue', 'attempts', 'reserved_at']);
echo 'Всего jobs: ' . \$jobs->count() . PHP_EOL;
foreach (\$jobs as \$job) {
    \$reserved = \$job->reserved_at ? 'reserved' : 'free';
    echo 'Job ID: ' . \$job->id . ', Attempts: ' . \$job->attempts . ', Status: ' . \$reserved . PHP_EOL;
}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        print("\n" + "="*60)
        print("✅ JOB ОСВОБОЖДЕН")
        print("="*60)
        print("\n💡 Queue worker должен обработать job заново с новым кодом")
        print("   Пентест должен продолжить работу")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    release_job()

