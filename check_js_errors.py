#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка JavaScript файла на ошибки
"""

import requests
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "https://72.56.79.153"

# Отключаем предупреждения о SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_js_file():
    """Проверка JavaScript файла"""
    print("="*70)
    print("ПРОВЕРКА JAVASCRIPT ФАЙЛА НА ОШИБКИ")
    print("="*70)
    
    # Получаем HTML
    try:
        response = requests.get(f"{BASE_URL}/app/", verify=False, timeout=10)
        html = response.text
        
        # Извлекаем путь к JS файлу
        import re
        js_match = re.search(r'src="([^"]+\.js[^"]*)"', html)
        
        if not js_match:
            print("✗ JS файл не найден в HTML")
            return
        
        js_path = js_match.group(1)
        js_url = f"{BASE_URL}{js_path}"
        
        print(f"\n1. ЗАГРУЗКА JS ФАЙЛА:")
        print("-" * 70)
        print(f"  URL: {js_url}")
        
        js_response = requests.get(js_url, verify=False, timeout=10)
        
        if js_response.status_code != 200:
            print(f"  ✗ Ошибка загрузки: {js_response.status_code}")
            return
        
        js_content = js_response.text
        print(f"  Размер: {len(js_content)} байт")
        print(f"  Content-Type: {js_response.headers.get('Content-Type', 'не указан')}")
        
        # Проверяем начало файла
        print(f"\n2. АНАЛИЗ НАЧАЛА ФАЙЛА:")
        print("-" * 70)
        first_500 = js_content[:500]
        print(f"  Первые 500 символов:")
        print(f"  {first_500}")
        
        # Проверяем на наличие ошибок
        print(f"\n3. ПРОВЕРКА НА ОШИБКИ:")
        print("-" * 70)
        
        error_patterns = [
            ('<!doctype', 'HTML вместо JavaScript'),
            ('<html', 'HTML вместо JavaScript'),
            ('<body', 'HTML вместо JavaScript'),
            ('SyntaxError', 'Синтаксическая ошибка'),
            ('ReferenceError', 'Ошибка ссылки'),
            ('TypeError', 'Ошибка типа'),
        ]
        
        found_errors = []
        for pattern, desc in error_patterns:
            if pattern.lower() in js_content.lower():
                found_errors.append((pattern, desc))
                print(f"  ✗ Найдено: {desc} ({pattern})")
        
        if not found_errors:
            print(f"  ✓ Очевидных ошибок не найдено")
        
        # Проверяем структуру файла
        print(f"\n4. ПРОВЕРКА СТРУКТУРЫ:")
        print("-" * 70)
        
        checks = {
            'import ': 'ES6 импорты',
            'export ': 'ES6 экспорты',
            'function': 'Функции',
            'const ': 'Константы',
            'var ': 'Переменные',
            'React': 'React',
        }
        
        for check, desc in checks.items():
            count = js_content.count(check)
            if count > 0:
                print(f"  ✓ {desc}: найдено {count} вхождений")
            else:
                print(f"  ⚠ {desc}: не найдено")
        
        # Проверяем конец файла
        print(f"\n5. АНАЛИЗ КОНЦА ФАЙЛА:")
        print("-" * 70)
        last_500 = js_content[-500:]
        print(f"  Последние 500 символов:")
        print(f"  {last_500}")
        
        # Проверяем на незакрытые скобки/кавычки
        print(f"\n6. ПРОВЕРКА СИНТАКСИСА:")
        print("-" * 70)
        
        open_braces = js_content.count('{')
        close_braces = js_content.count('}')
        open_parens = js_content.count('(')
        close_parens = js_content.count(')')
        open_brackets = js_content.count('[')
        close_brackets = js_content.count(']')
        
        print(f"  Фигурные скобки: {{ {open_braces} / }} {close_braces}")
        if open_braces == close_braces:
            print(f"    ✓ Сбалансированы")
        else:
            print(f"    ✗ НЕ сбалансированы!")
        
        print(f"  Круглые скобки: ( {open_parens} / ) {close_parens}")
        if open_parens == close_parens:
            print(f"    ✓ Сбалансированы")
        else:
            print(f"    ✗ НЕ сбалансированы!")
        
        print(f"  Квадратные скобки: [ {open_brackets} / ] {close_brackets}")
        if open_brackets == close_brackets:
            print(f"    ✓ Сбалансированы")
        else:
            print(f"    ✗ НЕ сбалансированы!")
        
        # Проверяем на наличие минификации
        if len(js_content) > 100000:
            print(f"\n  ✓ Файл минифицирован (большой размер)")
        else:
            print(f"\n  ⚠ Файл может быть не минифицирован")
        
    except Exception as e:
        print(f"✗ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

def check_html_structure():
    """Проверка структуры HTML"""
    print("\n" + "="*70)
    print("ПРОВЕРКА СТРУКТУРЫ HTML")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/app/", verify=False, timeout=10)
        html = response.text
        
        print(f"\n1. ПОЛНЫЙ HTML:")
        print("-" * 70)
        print(html)
        
        # Проверяем, что все теги закрыты
        print(f"\n2. ПРОВЕРКА ЗАКРЫТИЯ ТЕГОВ:")
        print("-" * 70)
        
        import re
        open_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*>', html)
        close_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9]*)>', html)
        
        print(f"  Открывающих тегов: {len(open_tags)}")
        print(f"  Закрывающих тегов: {len(close_tags)}")
        
        # Проверяем критически важные теги
        critical_tags = ['html', 'head', 'body', 'div', 'script']
        for tag in critical_tags:
            open_count = html.count(f'<{tag}')
            close_count = html.count(f'</{tag}>')
            if open_count == close_count:
                print(f"    ✓ Тег <{tag}> сбалансирован ({open_count}/{close_count})")
            else:
                print(f"    ✗ Тег <{tag}> НЕ сбалансирован ({open_count}/{close_count})")
        
    except Exception as e:
        print(f"✗ Ошибка: {str(e)}")

def main():
    check_js_file()
    check_html_structure()
    
    print("\n" + "="*70)
    print("РЕКОМЕНДАЦИИ")
    print("="*70)
    print("1. Откройте страницу в браузере")
    print("2. Откройте консоль разработчика (F12)")
    print("3. Проверьте вкладку Console на наличие ошибок")
    print("4. Проверьте вкладку Network - все ли файлы загружаются")
    print("5. Проверьте вкладку Elements - есть ли элемент #root")
    print("="*70)

if __name__ == "__main__":
    main()


