#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пересборка и развертывание frontend на сервере
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def rebuild_frontend():
    """Пересобирает frontend на сервере"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔨 Пересборка frontend на сервере...")
        print("="*60)
        
        # 1. Проверяем текущую директорию
        print("\n1. Проверка текущего состояния...")
        output, _, _ = conn.execute('cd /root/shannon/template && pwd')
        print(f"   Рабочая директория: {output.strip()}")
        
        # 2. Копируем исправленный api.ts на сервер
        print("\n2. Копирование исправленного api.ts...")
        with open('template/src/services/api.ts', 'r', encoding='utf-8') as f:
            api_content = f.read()
        
        # Сохраняем на сервере
        conn.execute(f'cat > /tmp/api.ts << \'API_EOF\'\n{api_content}\nAPI_EOF')
        conn.execute('cp /tmp/api.ts /root/shannon/template/src/services/api.ts')
        print("   ✅ api.ts обновлен")
        
        # 3. Пересобираем frontend
        print("\n3. Пересборка frontend...")
        output, error, code = conn.execute('cd /root/shannon/template && npm run build 2>&1')
        print(output[-500:] if len(output) > 500 else output)
        
        if code == 0:
            print("   ✅ Frontend успешно собран")
        else:
            print(f"   ❌ Ошибка сборки: {error}")
            return False
        
        # 4. Проверяем новые файлы
        print("\n4. Проверка собранных файлов...")
        output, _, _ = conn.execute('ls -lh /root/shannon/template/dist/assets/ | grep index')
        print(output)
        
        # 5. Проверяем содержимое index.html
        print("\n5. Проверка index.html...")
        output, _, _ = conn.execute('head -20 /root/shannon/template/dist/index.html')
        print(output)
        
        print("\n" + "="*60)
        print("✅ Frontend пересобран и готов к использованию!")
        print("="*60)
        print("\n💡 Теперь обновите страницу в браузере (Ctrl+F5)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = rebuild_frontend()
    sys.exit(0 if success else 1)

