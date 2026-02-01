#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка доступа Ollama к интернету
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_ollama_internet():
    """Проверяет доступ Ollama к интернету"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 ПРОВЕРКА ДОСТУПА OLLAMA К ИНТЕРНЕТУ")
        print("="*60)
        
        # 1. Проверяем статус Ollama
        print("\n1. Статус Ollama:")
        output, _, _ = conn.execute('systemctl status ollama.service --no-pager | head -15')
        print(output)
        
        # 2. Проверяем конфигурацию Ollama
        print("\n2. Конфигурация Ollama:")
        output, _, _ = conn.execute('cat /etc/systemd/system/ollama.service 2>&1 | head -20')
        print(output)
        
        # 3. Проверяем переменные окружения Ollama
        print("\n3. Переменные окружения Ollama:")
        output, _, _ = conn.execute('systemctl show ollama.service | grep -i "environment\|exec"')
        print(output)
        
        # 4. Проверяем может ли Ollama делать запросы в интернет
        print("\n4. Тест доступа Ollama к интернету:")
        print("   Проверяем может ли сервер делать HTTP запросы...")
        output, _, code = conn.execute('curl -s --max-time 5 https://www.google.com | head -1')
        if code == 0 and output:
            print("   ✅ Сервер имеет доступ к интернету")
        else:
            print("   ❌ Сервер не может подключиться к интернету")
        
        # 5. Проверяем настройки сети Ollama
        print("\n5. Настройки сети Ollama:")
        output, _, _ = conn.execute('curl -s http://localhost:11434/api/tags 2>&1 | head -5')
        if output:
            print("   ✅ Ollama API доступен локально")
            print(f"   Ответ: {output[:200]}")
        
        # 6. Проверяем может ли Ollama делать внешние запросы через API
        print("\n6. Тест внешних запросов через Ollama:")
        print("   Создаем тестовый запрос к Ollama с промптом о интернете...")
        test_prompt = '''{"model": "llama3.2:3b", "prompt": "What is the current date? Can you access the internet?", "stream": false}'''
        output, _, code = conn.execute(f"curl -s -X POST http://localhost:11434/api/generate -d '{test_prompt}' 2>&1 | head -10")
        if output:
            print(f"   Ответ Ollama: {output[:300]}")
        
        # 7. Проверяем конфигурационные файлы Ollama
        print("\n7. Конфигурационные файлы Ollama:")
        ollama_config_paths = [
            '/root/.ollama/config.json',
            '/etc/ollama/config.json',
            '~/.ollama/config.json'
        ]
        for path in ollama_config_paths:
            output, _, code = conn.execute(f"test -f {path} && cat {path} || echo 'not found'")
            if 'not found' not in output:
                print(f"   Найден конфиг: {path}")
                print(f"   {output[:200]}")
        
        # 8. Проверяем сетевые ограничения
        print("\n8. Сетевые ограничения:")
        output, _, _ = conn.execute('iptables -L -n 2>&1 | head -10')
        if output and 'iptables' not in output.lower():
            print("   ✅ Нет правил iptables блокирующих интернет")
        else:
            print("   ⚠️  Проверьте правила iptables")
        
        # 9. Проверяем DNS
        print("\n9. Проверка DNS:")
        output, _, code = conn.execute('nslookup google.com 2>&1 | head -5')
        if code == 0:
            print("   ✅ DNS работает")
            print(output)
        else:
            print("   ⚠️  Проблемы с DNS")
        
        print("\n" + "="*60)
        print("📊 ИТОГИ ПРОВЕРКИ")
        print("="*60)
        print("\n💡 Важно:")
        print("   Ollama работает ЛОКАЛЬНО и не требует интернета для работы модели")
        print("   Но для получения актуальной информации об уязвимостях может потребоваться интернет")
        print("   Проверьте может ли сервер делать HTTP запросы к внешним ресурсам")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_ollama_internet()

