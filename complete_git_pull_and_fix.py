#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Завершение git pull и исправление экспорта
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def complete_fix():
    """Завершает git pull и исправляет проблемы"""
    print("Завершение git pull и исправление...")
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # Удаляем конфликтующие файлы и делаем git pull
        print("\n[1] Удаление конфликтующих файлов и git pull...")
        conn.execute("cd /root/shannon && rm -f template/src/components/LogViewer.tsx template/src/utils/severity.ts && git pull origin master")
        
        # Проверяем экспорт в Pentests.tsx
        print("\n[2] Проверка экспорта в Pentests.tsx...")
        output, error, code = conn.execute("cd /root/shannon && tail -5 template/src/pages/Pentests.tsx")
        print(output)
        
        # Проверяем наличие export default
        output, error, code = conn.execute("cd /root/shannon && grep -n 'export default' template/src/pages/Pentests.tsx")
        print(f"Найденные экспорты: {output}")
        
        # Если нет export default, добавляем
        if not output or 'export default' not in output:
            print("\n[3] Добавление export default...")
            # Читаем последнюю строку
            output, error, code = conn.execute("cd /root/shannon && tail -1 template/src/pages/Pentests.tsx")
            if output and 'export default' not in output:
                conn.execute("cd /root/shannon && echo '' >> template/src/pages/Pentests.tsx && echo 'export default Pentests;' >> template/src/pages/Pentests.tsx")
        
        # Пересборка
        print("\n[4] Пересборка фронтенда...")
        output, error, code = conn.execute("cd /root/shannon/template && npm run build 2>&1")
        
        if output:
            lines = output.split('\n')
            if 'ERROR' in output or 'error' in output.lower() or code != 0:
                print('\n'.join(lines[-50:]))
            else:
                print('\n'.join(lines[-20:]))
        
        if code == 0:
            print("\n[OK] Фронтенд успешно собран!")
            
            # Проверка
            output, error, code = conn.execute("test -f /root/shannon/template/dist/index.html && ls -lh /root/shannon/template/dist/index.html || echo 'NOT FOUND'")
            print(f"\n[5] Результат:\n{output}")
            
            return True
        else:
            print("\n[ERROR] Ошибка сборки!")
            return False

if __name__ == "__main__":
    success = complete_fix()
    sys.exit(0 if success else 1)


