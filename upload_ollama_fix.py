#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка исправленного OllamaApiService на сервер
"""

import sys
import os
import base64

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def upload_fix():
    """Загружает исправление"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("📤 Загрузка исправления OllamaApiService...")
        print("="*60)
        
        # Читаем локальный файл
        with open('backend-laravel/app/Services/OllamaApiService.php', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Сохраняем на сервере через base64
        print("\n1. Сохранение файла на сервере...")
        content_b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
        
        cmd = f'''python3 << 'PYEOF'
import base64
content = base64.b64decode('{content_b64}').decode('utf-8')
with open('/tmp/OllamaApiService.php', 'w', encoding='utf-8') as f:
    f.write(content)
PYEOF'''
        conn.execute(cmd)
        
        # Копируем в нужное место
        conn.execute('cp /tmp/OllamaApiService.php /root/shannon/backend-laravel/app/Services/OllamaApiService.php')
        print("   ✅ Файл загружен")
        
        # Проверяем что исправление применено
        print("\n2. Проверка исправления...")
        output, _, _ = conn.execute('grep -n "vulnerabilities.*\[\]" /root/shannon/backend-laravel/app/Services/OllamaApiService.php | head -2')
        if output:
            print("   ✅ Исправление найдено")
        else:
            print("   ⚠️  Исправление не найдено")
        
        # Очищаем кэш
        print("\n3. Очистка кэша...")
        conn.execute('cd /root/shannon/backend-laravel && php artisan config:clear && php artisan cache:clear')
        print("   ✅ Кэш очищен")
        
        print("\n" + "="*60)
        print("✅ Исправление применено!")
        print("="*60)
        print("\n💡 Теперь Ollama будет лучше обрабатывать ответы:")
        print("   - Улучшен парсинг JSON")
        print("   - Улучшен промпт для более точных ответов")
        print("   - Обработка случаев когда уязвимостей нет")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    upload_fix()

