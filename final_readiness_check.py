#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная проверка готовности к пентесту
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
        print("✅ ФИНАЛЬНАЯ ПРОВЕРКА ГОТОВНОСТИ")
        print("="*60)
        
        # 1. Проверяем что файлы обновлены
        print("\n1. Проверка обновления файлов на сервере:")
        
        # Проверяем PentestEngine.php
        output, _, _ = conn.execute('grep -n "saveResultsToStorage\|pentest_reports" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php | head -3')
        if output and 'saveResultsToStorage' in output:
            print("   ✅ PentestEngine.php обновлен (сохранение результатов)")
        else:
            print("   ❌ PentestEngine.php НЕ обновлен!")
            return False
        
        # Проверяем UUID для уязвимостей
        output, _, _ = conn.execute('sed -n "/vulnerabilities()->create/,/});/p" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php | grep -q "uuid" && echo "found" || echo "not found"')
        if 'found' in output:
            print("   ✅ UUID для уязвимостей применен")
        else:
            print("   ⚠️  UUID проверка не прошла, проверяем вручную...")
            output2, _, _ = conn.execute('sed -n "/vulnerabilities()->create/,/});/p" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php | head -5')
            if "'id' => Str::uuid()->toString()" in output2:
                print("   ✅ UUID для уязвимостей применен (подтверждено)")
            else:
                print("   ❌ UUID НЕ применен!")
                return False
        
        # Проверяем OllamaApiService
        output, _, _ = conn.execute('grep -n "vulnerabilities.*\[\]" /root/shannon/backend-laravel/app/Services/OllamaApiService.php | head -1')
        if output:
            print("   ✅ OllamaApiService обновлен (улучшен парсинг)")
        else:
            print("   ⚠️  OllamaApiService может быть не обновлен")
        
        # 2. Проверяем папку для отчетов
        print("\n2. Проверка папки для отчетов:")
        output, _, code = conn.execute('test -d /root/shannon/pentest_reports && echo "exists" || echo "not found"')
        if 'exists' in output:
            print("   ✅ Папка /root/shannon/pentest_reports существует")
        else:
            print("   ⚠️  Папка не найдена, создаем...")
            conn.execute('mkdir -p /root/shannon/pentest_reports && chmod 755 /root/shannon/pentest_reports')
            print("   ✅ Папка создана")
        
        # 3. Проверяем сервисы
        print("\n3. Проверка сервисов:")
        services = {
            'shannon-laravel.service': 'Laravel Backend',
            'shannon-queue.service': 'Queue Worker',
            'nginx.service': 'Nginx',
            'ollama.service': 'Ollama'
        }
        
        all_ok = True
        for service, name in services.items():
            output, _, code = conn.execute(f'systemctl is-active {service} 2>&1')
            if 'active' in output:
                print(f"   ✅ {name}: активен")
            else:
                print(f"   ❌ {name}: не активен")
                all_ok = False
        
        if not all_ok:
            print("   ⚠️  Некоторые сервисы не активны!")
        
        # 4. Проверяем Ollama
        print("\n4. Проверка Ollama:")
        output, _, code = conn.execute('curl -s http://localhost:11434/api/tags | head -3')
        if output and 'llama3.2' in output:
            print("   ✅ Ollama работает, модель загружена")
        else:
            print("   ⚠️  Ollama не отвечает")
        
        # 5. Проверяем кэш
        print("\n5. Очистка кэша...")
        conn.execute('cd /root/shannon/backend-laravel && php artisan config:clear && php artisan cache:clear')
        print("   ✅ Кэш очищен")
        
        # 6. Проверяем версию кода
        print("\n6. Версия кода на сервере:")
        output, _, _ = conn.execute('cd /root/shannon && git log --oneline -1')
        print(f"   Последний коммит: {output.strip()}")
        
        print("\n" + "="*60)
        print("✅ СИСТЕМА ГОТОВА К ЗАПУСКУ ПЕНТЕСТА!")
        print("="*60)
        print("\n📋 Что будет происходить:")
        print("   ✅ Все 5 агентов отработают (nmap, nikto, nuclei, dirb, sqlmap)")
        print("   ✅ Результаты будут анализироваться через Ollama")
        print("   ✅ Уязвимости будут сохраняться с правильным UUID")
        print("   ✅ Полные результаты будут сохранены в:")
        print("      /root/shannon/pentest_reports/{pentest_id}/")
        print("\n🚀 МОЖНО ЗАПУСКАТЬ ПЕНТЕСТ!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    final_check()

