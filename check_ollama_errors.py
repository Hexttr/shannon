#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка ошибок Ollama в логах
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_ollama_errors():
    """Проверяет ошибки Ollama"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 Проверка ошибок Ollama...")
        print("="*60)
        
        # 1. Проверяем все ошибки Ollama в логах Laravel
        print("\n1. Все ошибки Ollama в логах Laravel:")
        output, _, _ = conn.execute('grep -i "ollama" /root/shannon/backend-laravel/storage/logs/laravel.log | tail -30')
        if output.strip():
            print(output)
        else:
            print("   Нет ошибок")
        
        # 2. Проверяем последние ошибки анализа
        print("\n2. Последние ошибки анализа:")
        output, _, _ = conn.execute('grep -i "ошибка анализа\|error.*ollama\|ollama.*error" /root/shannon/backend-laravel/storage/logs/laravel.log | tail -20')
        if output.strip():
            print(output)
        else:
            print("   Нет ошибок анализа")
        
        # 3. Проверяем логи пентеста с ошибками
        print("\n3. Ошибки в логах пентеста:")
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$pentest = App\\\\Models\\\\Pentest::orderBy('created_at', 'desc')->first();
if (\$pentest) {
    \$logs = \$pentest->logs()->where('level', 'error')->orderBy('created_at', 'desc')->get(['message', 'created_at']);
    echo 'Error logs: ' . \$logs->count() . PHP_EOL;
    foreach (\$logs->take(10) as \$log) {
        echo \$log->message . PHP_EOL;
        echo '---' . PHP_EOL;
    }
}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        # 4. Тестируем запрос к Ollama с реальным промптом
        print("\n4. Тест реального запроса к Ollama:")
        test_prompt = '''Проанализируй результаты сканирования безопасности для https://test.com/.

Инструмент: nmap

Результаты сканирования:
Starting Nmap 7.94SVN
PORT   STATE SERVICE
80/tcp open  http

Задача: Извлеки все найденные уязвимости безопасности и верни их ТОЛЬКО в формате JSON.

Формат ответа (обязательно строго соблюдай):
{
  "vulnerabilities": [
    {
      "title": "Название уязвимости",
      "description": "Подробное описание",
      "severity": "critical|high|medium|low",
      "cvss_score": "X.X",
      "cve": "CVE-XXXX-XXXX или пустая строка",
      "solution": "Рекомендации по исправлению"
    }
  ]
}

ВАЖНО:
1. Верни ТОЛЬКО валидный JSON объект
2. Если уязвимостей нет, верни: {"vulnerabilities": []}
3. НЕ добавляй никакого текста до или после JSON
4. НЕ используй markdown code blocks
5. Всегда возвращай массив vulnerabilities, даже если он пустой'''
        
        import json
        test_data = {
            "model": "llama3.2:3b",
            "messages": [{"role": "user", "content": test_prompt}],
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 4096}
        }
        
        test_json = json.dumps(test_data).replace("'", "'\\''")
        output, _, code = conn.execute(f"curl -s -X POST http://localhost:11434/api/chat -d '{test_json}' --max-time 30")
        
        if code == 0 and output:
            print("   ✅ Запрос выполнен")
            try:
                response = json.loads(output)
                content = response.get('message', {}).get('content', '')
                print(f"   Ответ (первые 500 символов): {content[:500]}")
                
                # Проверяем парсинг
                if 'vulnerabilities' in content.lower() or '{' in content:
                    print("   ✅ Ответ содержит JSON структуру")
                else:
                    print("   ⚠️  Ответ не содержит JSON структуру")
            except:
                print(f"   ⚠️  Не удалось распарсить ответ: {output[:200]}")
        else:
            print(f"   ❌ Ошибка запроса (code: {code})")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_ollama_errors()

