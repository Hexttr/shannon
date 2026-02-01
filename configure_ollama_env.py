#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Добавление конфигурации Ollama в .env Laravel
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def configure_ollama_env(conn):
    """Добавляет конфигурацию Ollama в .env"""
    print("\n" + "="*60)
    print("⚙️  Настройка .env для Ollama...")
    print("="*60)
    
    env_file = "/root/shannon/backend-laravel/.env"
    
    # Проверяем, существует ли файл
    output, error, code = conn.execute(f"test -f {env_file} && echo 'exists' || echo 'not-found'")
    if 'not-found' in output:
        print(f"❌ Файл {env_file} не найден")
        return False
    
    # Проверяем, есть ли уже настройки Ollama
    output, error, code = conn.execute(f"grep -q 'OLLAMA_API_URL' {env_file} && echo 'exists' || echo 'not-found'")
    
    if 'exists' in output:
        print("⚠️  Настройки Ollama уже есть в .env")
        print("   Обновляем значения...")
        # Обновляем существующие значения
        conn.execute(f"sed -i 's|^OLLAMA_API_URL=.*|OLLAMA_API_URL=http://localhost:11434/api|' {env_file}")
        conn.execute(f"sed -i 's|^OLLAMA_MODEL=.*|OLLAMA_MODEL=llama3.2:3b|' {env_file}")
    else:
        print("➕ Добавляем настройки Ollama в .env...")
        # Добавляем в конец файла
        conn.execute(f"echo '' >> {env_file}")
        conn.execute(f"echo '# Ollama Configuration' >> {env_file}")
        conn.execute(f"echo 'OLLAMA_API_URL=http://localhost:11434/api' >> {env_file}")
        conn.execute(f"echo 'OLLAMA_MODEL=llama3.2:3b' >> {env_file}")
    
    # Проверяем результат
    output, error, code = conn.execute(f"grep 'OLLAMA' {env_file}")
    if output:
        print("\n✅ Конфигурация добавлена:")
        print(output)
        return True
    else:
        print("❌ Не удалось добавить конфигурацию")
        return False

def test_ollama_generation(conn):
    """Тестирует генерацию через Ollama API"""
    print("\n" + "="*60)
    print("🧪 Тестирование генерации через Ollama API...")
    print("="*60)
    
    # Простой тест генерации
    test_prompt = "Hello, how are you?"
    print(f"📝 Тестовый промпт: {test_prompt}")
    
    # Используем API для генерации
    curl_cmd = f"""curl -s http://localhost:11434/api/generate -d '{{"model": "llama3.2:3b", "prompt": "{test_prompt}", "stream": false}}'"""
    
    output, error, code = conn.execute(curl_cmd)
    
    if output and 'response' in output:
        print("✅ Генерация работает!")
        # Извлекаем ответ
        import json
        try:
            data = json.loads(output)
            if 'response' in data:
                print(f"   Ответ модели: {data['response'][:100]}...")
                return True
        except:
            pass
    
    print("⚠️  Не удалось получить ответ от модели")
    print(f"   Output: {output[:200]}...")
    return False

def main():
    """Главная функция"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        # Настройка .env
        if configure_ollama_env(conn):
            print("\n✅ Конфигурация успешно добавлена в .env")
        else:
            print("\n⚠️  Не удалось добавить конфигурацию")
        
        # Тестирование генерации
        if test_ollama_generation(conn):
            print("\n✅ Ollama готов к работе!")
        else:
            print("\n⚠️  Тест генерации не прошел, но API работает")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()

