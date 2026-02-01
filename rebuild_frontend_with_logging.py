#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пересборка frontend с логированием для отладки
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def rebuild_with_logging():
    """Пересобирает frontend с логированием"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔨 Пересборка frontend с логированием...")
        print("="*60)
        
        # Копируем исправленный api.ts на сервер
        print("\n1. Копирование исправленного api.ts...")
        with open('template/src/services/api.ts', 'r', encoding='utf-8') as f:
            api_content = f.read()
        
        conn.execute(f'cat > /tmp/api.ts << \'API_EOF\'\n{api_content}\nAPI_EOF')
        conn.execute('cp /tmp/api.ts /root/shannon/template/src/services/api.ts')
        print("   ✅ api.ts обновлен")
        
        # Пересобираем frontend
        print("\n2. Пересборка frontend...")
        output, error, code = conn.execute('cd /root/shannon/template && npm run build 2>&1')
        print(output[-500:] if len(output) > 500 else output)
        
        if code == 0:
            print("   ✅ Frontend успешно собран")
        else:
            print(f"   ❌ Ошибка сборки: {error}")
            return False
        
        # Проверяем новый файл
        print("\n3. Проверка нового файла...")
        output, _, _ = conn.execute('ls -lh /root/shannon/template/dist/assets/index-*.js | tail -1')
        latest_file = output.split()[-1] if output else None
        if latest_file:
            print(f"   Новый файл: {latest_file}")
            
            # Проверяем что старый URL не используется
            output, _, _ = conn.execute(f'grep -o "72.56.79.153:8000" {latest_file} | head -1')
            if output:
                print("   ⚠️  ВНИМАНИЕ: Старый URL все еще найден в файле!")
            else:
                print("   ✅ Старый URL не найден")
            
            # Проверяем что новый URL используется
            output, _, _ = conn.execute(f'grep -o "location.protocol" {latest_file} | head -1')
            if output:
                print("   ✅ Используется location.protocol")
            else:
                print("   ⚠️  location.protocol не найден")
        
        # Обновляем index.html
        print("\n4. Проверка index.html...")
        output, _, _ = conn.execute('cat /root/shannon/template/dist/index.html')
        if latest_file and latest_file.split('/')[-1] in output:
            print("   ✅ index.html ссылается на новый файл")
        else:
            print("   ⚠️  index.html может ссылаться на старый файл")
        
        print("\n" + "="*60)
        print("✅ Frontend пересобран!")
        print("="*60)
        print("\n💡 Инструкции:")
        print("   1. Очистите кэш браузера полностью (Ctrl+Shift+Delete)")
        print("   2. Или используйте режим инкогнито")
        print("   3. Откройте консоль браузера (F12)")
        print("   4. Проверьте логи с префиксом [API]")
        print("   5. Должно быть: API_URL: https://72.56.79.153/api")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    rebuild_with_logging()
