#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка и исправление проблемы с Ollama
"""

import sys
import os
import base64

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def verify_and_fix():
    """Проверяет и исправляет проблему"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 Проверка и исправление проблемы с Ollama...")
        print("="*60)
        
        # 1. Проверяем код на сервере
        print("\n1. Проверка кода PentestEngine на сервере:")
        output, _, _ = conn.execute('grep -A 5 "vulnerabilities()->create" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php | head -10')
        print(output)
        
        if "'id' => Str::uuid()->toString()" in output:
            print("   ✅ Исправление применено")
        else:
            print("   ❌ Исправление НЕ применено, загружаем...")
            # Загружаем исправленный файл
            with open('backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php', 'r', encoding='utf-8') as f:
                content = f.read()
            
            content_b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
            cmd = f'''python3 << 'PYEOF'
import base64
content = base64.b64decode('{content_b64}').decode('utf-8')
with open('/tmp/PentestEngine.php', 'w', encoding='utf-8') as f:
    f.write(content)
PYEOF'''
            conn.execute(cmd)
            conn.execute('cp /tmp/PentestEngine.php /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php')
            print("   ✅ Файл обновлен")
        
        # 2. Улучшаем парсинг Ollama для обработки markdown code blocks
        print("\n2. Улучшение парсинга Ollama...")
        with open('backend-laravel/app/Services/OllamaApiService.php', 'r', encoding='utf-8') as f:
            ollama_content = f.read()
        
        # Улучшаем удаление markdown code blocks
        if 'preg_replace.*```json' in ollama_content and 'preg_replace.*```[^j]' in ollama_content:
            # Улучшаем парсинг - удаляем все markdown code blocks более агрессивно
            old_parse = '''        // Удаляем markdown code blocks если есть
        $content = preg_replace('/```json\s*/', '', $content);
        $content = preg_replace('/```\s*/', '', $content);
        $content = trim($content);'''
            
            new_parse = '''        // Удаляем markdown code blocks если есть (более агрессивно)
        $content = preg_replace('/```json\s*/i', '', $content);
        $content = preg_replace('/```\s*/', '', $content);
        // Удаляем все что до первой { и после последней }
        if (preg_match('/\{.*\}/s', $content, $matches)) {
            $content = $matches[0];
        }
        $content = trim($content);'''
            
            if old_parse in ollama_content:
                ollama_content = ollama_content.replace(old_parse, new_parse)
                with open('backend-laravel/app/Services/OllamaApiService.php', 'w', encoding='utf-8') as f:
                    f.write(ollama_content)
                print("   ✅ Парсинг улучшен")
        
        # Загружаем улучшенный файл
        ollama_b64 = base64.b64encode(ollama_content.encode('utf-8')).decode('ascii')
        cmd = f'''python3 << 'PYEOF'
import base64
content = base64.b64decode('{ollama_b64}').decode('utf-8')
with open('/tmp/OllamaApiService.php', 'w', encoding='utf-8') as f:
    f.write(content)
PYEOF'''
        conn.execute(cmd)
        conn.execute('cp /tmp/OllamaApiService.php /root/shannon/backend-laravel/app/Services/OllamaApiService.php')
        print("   ✅ OllamaApiService обновлен")
        
        # 3. Очищаем кэш и перезапускаем queue worker
        print("\n3. Очистка кэша и перезапуск queue worker...")
        conn.execute('cd /root/shannon/backend-laravel && php artisan config:clear && php artisan cache:clear')
        conn.execute('systemctl restart shannon-queue.service')
        output, _, _ = conn.execute('sleep 2 && systemctl status shannon-queue.service --no-pager | head -10')
        print(output)
        
        print("\n" + "="*60)
        print("✅ Исправления применены!")
        print("="*60)
        print("\n💡 Теперь:")
        print("   - Уязвимости будут создаваться с правильным ID")
        print("   - Парсинг Ollama улучшен для обработки markdown")
        print("   - Queue worker перезапущен с новым кодом")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    verify_and_fix()

