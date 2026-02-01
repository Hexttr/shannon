#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Продвинутое исправление форматирования файлов
"""

import re
import os
from pathlib import Path

def fix_file_advanced(file_path):
    """Продвинутое исправление форматирования файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. Исправляем импорты - разделяем множественные импорты
        # Паттерн: import ...;import
        content = re.sub(r';(import\s+)', r';\n\1', content)
        
        # 2. Исправляем экспорты после импортов
        content = re.sub(r';(export\s+)', r';\n\1', content)
        
        # 3. Исправляем интерфейсы после импортов
        content = re.sub(r';(interface\s+)', r';\n\1', content)
        
        # 4. Исправляем const/let/var после импортов
        content = re.sub(r';(const\s+)', r';\n\1', content)
        content = re.sub(r';(let\s+)', r';\n\1', content)
        content = re.sub(r';(var\s+)', r';\n\1', content)
        
        # 5. Исправляем функции после других конструкций
        content = re.sub(r'(\})\s*(function\s+)', r'\1\n\2', content)
        content = re.sub(r'(\})\s*(export\s+default\s+function)', r'\1\n\2', content)
        
        # 6. Исправляем интерфейсы и типы
        content = re.sub(r'(\})\s*(interface\s+)', r'\1\n\2', content)
        content = re.sub(r'(\})\s*(type\s+)', r'\1\n\2', content)
        
        # 7. Исправляем объявления массивов/объектов
        content = re.sub(r'(\]\s*=\s*\[)', r'\1\n  ', content)
        content = re.sub(r'(\}\s*=\s*\{)', r'\1\n  ', content)
        
        # 8. Исправляем множественные объявления в одной строке
        # Паттерн: }const menuItems = [
        content = re.sub(r'(\})\s*(const\s+\w+\s*=\s*\[)', r'\1\n\2', content)
        content = re.sub(r'(\])\s*(interface\s+)', r'\1\n\2', content)
        
        # 9. Исправляем JSX компоненты
        content = re.sub(r'(\])\s*(export\s+default)', r'\1\n\n\2', content)
        content = re.sub(r'(\})\s*(export\s+default)', r'\1\n\n\2', content)
        
        # 10. Исправляем множественные объявления в интерфейсах
        # Паттерн: interface X {  path: string;  label: string;}
        content = re.sub(r'(\w+:\s*[^;]+);(\s+\w+:)', r'\1;\n  \2', content)
        
        # 11. Исправляем массивы объектов
        # Паттерн: { path: '/home', label: 'Главная' }, { path: '/services'
        content = re.sub(r'(\}\s*),\s*(\{)', r'\1},\n  \2', content)
        
        # 12. Убираем множественные пробелы в начале строк
        lines = content.split('\n')
        fixed_lines = []
        for i, line in enumerate(lines):
            # Если строка не пустая и начинается с пробела, но не с правильного отступа
            if line.strip() and line.startswith(' ') and not line.startswith('  '):
                # Проверяем контекст
                if i > 0 and lines[i-1].strip().endswith('{'):
                    fixed_lines.append('  ' + line.lstrip())
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # 13. Убираем множественные пустые строки
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 14. Исправляем финальные проблемы с закрывающими скобками
        # Паттерн: }export default
        content = re.sub(r'(\})\s*(export\s+default)', r'\1\n\n\2', content)
        
        # Если файл изменился, сохраняем
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"  [ERROR] {file_path}: {e}")
        return False

def main():
    print("="*60)
    print("ПРОДВИНУТОЕ ИСПРАВЛЕНИЕ ФОРМАТИРОВАНИЯ")
    print("="*60)
    
    template_dir = Path("template/src")
    
    # Список файлов для исправления
    files_to_fix = [
        "components/Sidebar.tsx",
        "components/Layout.tsx",
        "components/VulnerabilitiesList.tsx",
        "pages/Analytics.tsx",
        "pages/Pentests.tsx",
        "pages/Dashboard.tsx",
        "pages/Reports.tsx",
        "pages/Home.tsx",
        "pages/Services.tsx",
    ]
    
    fixed_count = 0
    for file_rel_path in files_to_fix:
        file_path = template_dir / file_rel_path
        if file_path.exists():
            print(f"\nИсправление: {file_rel_path}")
            if fix_file_advanced(file_path):
                print(f"  [OK] Исправлен")
                fixed_count += 1
            else:
                print(f"  [SKIP] Не требует исправления")
        else:
            print(f"\n  [WARNING] Файл не найден: {file_rel_path}")
    
    print("\n" + "="*60)
    print(f"ГОТОВО! Исправлено файлов: {fixed_count}")
    print("="*60)

if __name__ == "__main__":
    main()


