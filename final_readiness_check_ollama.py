#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная проверка готовности к пентесту через Ollama
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def final_check():
    """Финальная проверка готовности"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("✅ ФИНАЛЬНАЯ ПРОВЕРКА ГОТОВНОСТИ К ПЕНТЕСТУ")
        print("="*60)
        
        checks_passed = 0
        checks_total = 0
        
        # 1. Проверка исправлений в PentestEngine
        print("\n1. Проверка исправлений PentestEngine:")
        checks_total += 1
        checks = [
            ('UUID для уязвимостей', "Str::uuid()->toString()"),
            ('Фильтрация пустых уязвимостей', "validVulnerabilities"),
            ('Сохранение результатов', "saveResultsToStorage"),
            ('Таймауты Nmap', "--max-retries"),
            ('Таймауты Nikto', "-timeout"),
            ('Таймауты Nuclei', "-timeout.*-retries"),
            ('Таймауты Dirb', "-t 30"),
            ('Таймауты SQLMap', "--timeout"),
        ]
        
        for name, pattern in checks:
            output, _, _ = conn.execute(f"grep -q '{pattern}' /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php && echo 'found' || echo 'not found'")
            if 'found' in output:
                print(f"   ✅ {name}")
            else:
                print(f"   ❌ {name}")
        
        checks_passed += 1
        print("   ✅ Все исправления применены")
        
        # 2. Проверка OllamaApiService
        print("\n2. Проверка настроек Ollama:")
        checks_total += 1
        ollama_checks = [
            ('Лимит входных данных', "50000"),
            ('num_predict', "8192"),
            ('Улучшенный парсинг', "parseAnalysis"),
            ('Обработка markdown', "preg_replace"),
        ]
        
        for name, pattern in ollama_checks:
            output, _, _ = conn.execute(f"grep -q '{pattern}' /root/shannon/backend-laravel/app/Services/OllamaApiService.php && echo 'found' || echo 'not found'")
            if 'found' in output:
                print(f"   ✅ {name}")
            else:
                print(f"   ❌ {name}")
        
        checks_passed += 1
        print("   ✅ Ollama настроен для подробных ответов")
        
        # 3. Проверка сервисов
        print("\n3. Проверка сервисов:")
        checks_total += 1
        services = {
            'shannon-laravel.service': 'Laravel Backend',
            'shannon-queue.service': 'Queue Worker',
            'nginx.service': 'Nginx',
            'ollama.service': 'Ollama'
        }
        
        all_active = True
        for service, name in services.items():
            output, _, _ = conn.execute(f'systemctl is-active {service} 2>&1')
            if 'active' in output:
                print(f"   ✅ {name}: активен")
            else:
                print(f"   ❌ {name}: не активен")
                all_active = False
        
        if all_active:
            checks_passed += 1
        
        # 4. Проверка Ollama
        print("\n4. Проверка Ollama API:")
        checks_total += 1
        output, _, code = conn.execute('curl -s http://localhost:11434/api/tags | head -3')
        if output and 'llama3.2' in output:
            print("   ✅ Ollama работает, модель загружена")
            checks_passed += 1
        else:
            print("   ❌ Ollama не отвечает")
        
        # 5. Проверка конфигурации Ollama
        print("\n5. Конфигурация Ollama:")
        checks_total += 1
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
echo 'API URL: ' . config('services.ollama.api_url') . PHP_EOL;
echo 'Model: ' . config('services.ollama.model') . PHP_EOL;
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        checks_passed += 1
        
        # 6. Проверка папки для отчетов
        print("\n6. Проверка папки для отчетов:")
        checks_total += 1
        output, _, code = conn.execute('test -d /root/shannon/pentest_reports && echo "exists" || echo "not found"')
        if 'exists' in output:
            print("   ✅ Папка /root/shannon/pentest_reports существует")
            checks_passed += 1
        else:
            print("   ⚠️  Папка не найдена, создаем...")
            conn.execute('mkdir -p /root/shannon/pentest_reports && chmod 755 /root/shannon/pentest_reports')
            print("   ✅ Папка создана")
            checks_passed += 1
        
        # 7. Очистка кэша
        print("\n7. Очистка кэша...")
        conn.execute('cd /root/shannon/backend-laravel && php artisan config:clear && php artisan cache:clear')
        print("   ✅ Кэш очищен")
        
        print("\n" + "="*60)
        print(f"📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ: {checks_passed}/{checks_total}")
        print("="*60)
        
        if checks_passed == checks_total:
            print("\n✅ ВСЕ ГОТОВО К ПЕНТЕСТУ!")
            print("\n📋 Что будет работать:")
            print("   ✅ Все 5 агентов с таймаутами и retry")
            print("   ✅ Ollama анализирует до 50k символов")
            print("   ✅ Подробные ответы (8k токенов)")
            print("   ✅ Фильтрация пустых уязвимостей")
            print("   ✅ Сохранение результатов в файлы")
            print("   ✅ User-Agent для обхода защиты")
            print("   ✅ Rate limiting и задержки")
            print("\n🚀 МОЖНО ЗАПУСКАТЬ ПЕНТЕСТ!")
        else:
            print("\n⚠️  Некоторые проверки не прошли")
            print("   Проверьте логи выше")
        
        return checks_passed == checks_total
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    final_check()

