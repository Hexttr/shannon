#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка проблемы с парсингом Ollama
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_parsing():
    """Проверяет проблему с парсингом"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 ПРОВЕРКА ПРОБЛЕМЫ С ПАРСИНГОМ OLLAMA")
        print("="*60)
        
        # Проверяем логи с предупреждениями Ollama
        print("\n1. Логи с предупреждениями Ollama:")
        output, _, _ = conn.execute('grep -i "ollama.*не удалось\|ollama.*warning\|ollama.*error" /root/shannon/backend-laravel/storage/logs/laravel.log | tail -10')
        if output.strip():
            print(output)
        else:
            print("   Нет предупреждений")
        
        # Проверяем что возвращает Ollama для пустых уязвимостей
        print("\n2. Проверка уязвимостей с пустыми полями:")
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$pentest = App\\\\Models\\\\Pentest::orderBy('created_at', 'desc')->first();
if (\$pentest) {
    \$vulns = \$pentest->vulnerabilities()->where('title', '')->orWhere('title', null)->get(['id', 'title', 'severity', 'created_at']);
    echo 'Уязвимостей с пустым title: ' . \$vulns->count() . PHP_EOL;
    foreach (\$vulns as \$v) {
        echo 'ID: ' . \$v->id . ', Created: ' . \$v->created_at . PHP_EOL;
    }
}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        print("\n" + "="*60)
        print("💡 ПРОБЛЕМА:")
        print("="*60)
        print("Уязвимости создаются с пустыми полями.")
        print("Это означает что Ollama возвращает JSON с пустыми значениями")
        print("или парсинг не извлекает данные правильно.")
        print("\nНужно проверить:")
        print("1. Что возвращает Ollama (логи)")
        print("2. Как парсится JSON (может быть пустые объекты)")
        print("3. Добавить валидацию - не создавать уязвимости с пустыми полями")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_parsing()

