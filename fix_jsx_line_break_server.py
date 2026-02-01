#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление форматирования Pentests.tsx на сервере через Python
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def fix_jsx_on_server():
    """Исправляет JSX на сервере через Python скрипт"""
    print("Исправление форматирования через Python на сервере...")
    
    python_script = '''
import re

file_path = "/root/shannon/template/src/pages/Pentests.tsx"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Разбиваем длинную строку после комментария Header
content = re.sub(r'\{/\* Header \*/\}\s+<div', r'{/* Header */}\n      <div', content)

# Разбиваем после закрывающих тегов div (добавляем переносы)
content = re.sub(r'</div>\s+</div>\s+{/\*', r'</div>\n      </div>\n      {/*', content)
content = re.sub(r'</div>\s+</div>\s+<div', r'</div>\n      </div>\n      <div', content)

# Разбиваем после комментариев
content = re.sub(r'\{/\* Metrics \*/\}\s+<div', r'{/* Metrics */}\n      <div', content)
content = re.sub(r'\{/\* Dates \*/\}\s+<div', r'{/* Dates */}\n      <div', content)
content = re.sub(r'\{/\* Actions \*/\}\s+<div', r'{/* Actions */}\n      <div', content)
content = re.sub(r'\{/\* Expanded Content \*/\}\s+\{expanded', r'{/* Expanded Content */}\n      {expanded', content)

# Разбиваем длинные строки с множественными пробелами на отдельные строки
# Ищем паттерн: закрывающий тег + много пробелов + открывающий тег/комментарий
content = re.sub(r'(</div>)\s{6,}(<div|{/\*)', r'\\1\n      \\2', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Файл исправлен")
'''
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # Сохраняем Python скрипт на сервере и выполняем
        print("\n[1] Выполнение Python скрипта на сервере...")
        conn.execute(f"python3 << 'PYTHON_EOF'\n{python_script}\nPYTHON_EOF")
        
        # Проверяем результат
        output, error, code = conn.execute("cd /root/shannon && sed -n '119,121p' template/src/pages/Pentests.tsx")
        print(f"\n[2] Проверка строк 119-121:\n{output}")
        
        # Пересборка
        print("\n[3] Пересборка фронтенда...")
        output, error, code = conn.execute("cd /root/shannon/template && npm run build 2>&1")
        
        if output:
            lines = output.split('\n')
            if 'ERROR' in output or 'error' in output.lower() or code != 0:
                print('\n'.join(lines[-30:]))
            else:
                print('\n'.join(lines[-10:]))
        
        if code == 0:
            print("\n[OK] Фронтенд успешно собран!")
            output, error, code = conn.execute("test -f /root/shannon/template/dist/index.html && ls -lh /root/shannon/template/dist/index.html || echo 'NOT FOUND'")
            print(f"\n[4] Результат:\n{output}")
            return True
        else:
            print("\n[ERROR] Ошибка сборки!")
            return False

if __name__ == "__main__":
    success = fix_jsx_on_server()
    sys.exit(0 if success else 1)


