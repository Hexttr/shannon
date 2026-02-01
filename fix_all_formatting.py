#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление форматирования всех поврежденных файлов
"""

import re
import os
from pathlib import Path

def fix_file(file_path):
    """Исправляет форматирование файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Исправляем импорты - добавляем переносы строк
        # Паттерн: import ... from '...';import
        content = re.sub(r'(import\s+[^;]+);(import)', r'\1;\n\2', content)
        
        # Паттерн: import ... from '...';export
        content = re.sub(r'(import\s+[^;]+);(export)', r'\1;\n\2', content)
        
        # Паттерн: import ... from '...';const
        content = re.sub(r'(import\s+[^;]+);(const)', r'\1;\n\2', content)
        
        # Паттерн: import ... from '...';interface
        content = re.sub(r'(import\s+[^;]+);(interface)', r'\1;\n\2', content)
        
        # Паттерн: import ... from '...';function
        content = re.sub(r'(import\s+[^;]+);(function)', r'\1;\n\2', content)
        
        # Паттерн: import ... from '...';// TODO
        content = re.sub(r'(import\s+[^;]+);(//)', r'\1;\n\2', content)
        
        # Исправляем множественные импорты в одной строке
        # Паттерн: import { a, b } from 'x';import { c } from 'y';
        content = re.sub(r'(import\s+\{[^}]+\}\s+from\s+[\'"][^\'"]+[\'"]);(import)', r'\1;\n\2', content)
        
        # Исправляем экспорты
        content = re.sub(r'(export\s+default\s+function)', r'\n\1', content)
        content = re.sub(r'(export\s+default)', r'\n\1', content)
        
        # Исправляем интерфейсы
        content = re.sub(r'(interface\s+\w+)', r'\n\1', content)
        
        # Исправляем const/let/var объявления после импортов
        content = re.sub(r'(import\s+[^;]+);(\s*const\s+)', r'\1;\n\2', content)
        
        # Убираем лишние пробелы в начале строк
        lines = content.split('\n')
        fixed_lines = []
        for line in lines:
            # Если строка начинается с пробела после импорта, убираем его
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Убираем множественные пустые строки
        content = re.sub(r'\n{3,}', '\n\n', content)
        
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
    print("ИСПРАВЛЕНИЕ ФОРМАТИРОВАНИЯ ФАЙЛОВ")
    print("="*60)
    
    template_dir = Path("template/src")
    
    # Список файлов для исправления
    files_to_fix = [
        "components/Sidebar.tsx",
        "components/VulnerabilitiesList.tsx",
        "pages/Analytics.tsx",
        "pages/Pentests.tsx",
        "pages/Dashboard.tsx",
        "pages/Reports.tsx",
        "pages/Home.tsx",
        "pages/Services.tsx",  # На всякий случай
    ]
    
    fixed_count = 0
    for file_rel_path in files_to_fix:
        file_path = template_dir / file_rel_path
        if file_path.exists():
            print(f"\nИсправление: {file_rel_path}")
            if fix_file(file_path):
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



