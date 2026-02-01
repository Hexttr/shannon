#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление переносов строк в Pentests.tsx и пересборка
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def fix_line_breaks():
    """Исправляет переносы строк и пересобирает"""
    print("Исправление переносов строк...")
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # Используем sed для добавления переносов строк после закрывающих скобок и точек с запятой
        print("\n[1] Исправление переносов строк...")
        # Добавляем переносы после }); перед export
        conn.execute("cd /root/shannon && sed -i 's/});export default/});\n\nexport default/g' template/src/pages/Pentests.tsx")
        # Добавляем переносы после } перед export  
        conn.execute("cd /root/shannon && sed -i 's/^}export default/}\n\nexport default/g' template/src/pages/Pentests.tsx")
        
        # Проверяем результат
        output, error, code = conn.execute("cd /root/shannon && tail -3 template/src/pages/Pentests.tsx")
        print(f"Последние строки файла:\n{output}")
        
        # Пересборка
        print("\n[2] Пересборка фронтенда...")
        output, error, code = conn.execute("cd /root/shannon/template && npm run build 2>&1")
        
        if output:
            lines = output.split('\n')
            if 'ERROR' in output or 'error' in output.lower() or code != 0:
                print('\n'.join(lines[-30:]))
            else:
                print('\n'.join(lines[-10:]))
        
        if code == 0:
            print("\n[OK] Фронтенд успешно собран!")
            
            # Проверка
            output, error, code = conn.execute("test -f /root/shannon/template/dist/index.html && ls -lh /root/shannon/template/dist/index.html || echo 'NOT FOUND'")
            print(f"\n[3] Результат:\n{output}")
            
            return True
        else:
            print("\n[ERROR] Ошибка сборки!")
            return False

if __name__ == "__main__":
    success = fix_line_breaks()
    sys.exit(0 if success else 1)


