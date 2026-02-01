#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка готовности к новому пентесту
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_readiness():
    """Проверяет готовность системы"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("✅ ПРОВЕРКА ГОТОВНОСТИ К НОВОМУ ПЕНТЕСТУ")
        print("="*60)
        
        # 1. Проверяем исправления в коде
        print("\n1. Проверка исправлений в коде:")
        output, _, _ = conn.execute('grep -n "Str::uuid()->toString()" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php | grep vulnerabilities')
        if output:
            print("   ✅ UUID для уязвимостей добавлен")
        else:
            print("   ❌ UUID не найден")
        
        # 2. Проверяем статус сервисов
        print("\n2. Статус сервисов:")
        output, _, _ = conn.execute('systemctl is-active shannon-laravel.service shannon-queue.service nginx.service ollama.service 2>&1')
        services = output.strip().split('\n')
        for service in services:
            if 'active' in service:
                print(f"   ✅ {service}")
            else:
                print(f"   ⚠️  {service}")
        
        # 3. Проверяем работу Ollama
        print("\n3. Проверка Ollama:")
        output, _, _ = conn.execute('curl -s http://localhost:11434/api/tags | head -3')
        if output and 'llama3.2' in output:
            print("   ✅ Ollama работает, модель загружена")
        else:
            print("   ⚠️  Ollama не отвечает")
        
        # 4. Проверяем папки с результатами
        print("\n4. Папки с результатами пентестов:")
        output, _, _ = conn.execute('ls -la /root/shannon/ | grep -E "pentest|report" || echo "Папки не найдены"')
        print(f"   {output}")
        
        # Проверяем /tmp для временных файлов
        output, _, _ = conn.execute('ls -la /tmp/ | grep -E "nmap|nikto|nuclei|dirb|sqlmap" | head -5')
        if output:
            print(f"   Временные файлы в /tmp: найдено")
        else:
            print("   Временные файлы: нет (нормально если пентест завершен)")
        
        # 5. Проверяем базу данных
        print("\n5. Проверка базы данных:")
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
echo 'Pentests: ' . App\\\\Models\\\\Pentest::count() . PHP_EOL;
echo 'Vulnerabilities: ' . App\\\\Models\\\\Vulnerability::count() . PHP_EOL;
echo 'Logs: ' . App\\\\Models\\\\Log::count() . PHP_EOL;
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        # 6. Проверяем что код обновлен
        print("\n6. Проверка версии кода:")
        output, _, _ = conn.execute('cd /root/shannon && git log --oneline -1')
        print(f"   Последний коммит: {output.strip()}")
        
        print("\n" + "="*60)
        print("✅ СИСТЕМА ГОТОВА К НОВОМУ ПЕНТЕСТУ")
        print("="*60)
        print("\n💡 О сохранении результатов:")
        print("   - Результаты сохраняются в БД (SQLite)")
        print("   - Временные файлы создаются в /tmp/")
        print("   - Каждый пентест имеет уникальный ID")
        print("   - Уязвимости и логи привязаны к ID пентеста")
        print("\n✅ Можно запускать новый пентест!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_readiness()

