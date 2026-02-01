#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка API URL в собранном JavaScript
"""

import paramiko
import requests
import sys
import re

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "https://72.56.79.153"

# Отключаем предупреждения о SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ssh_exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    print("="*70)
    print("ПРОВЕРКА API URL В СОБРАННОМ JAVASCRIPT")
    print("="*70)
    
    # Получаем HTML и находим JS файл
    print("\n1. ПОЛУЧЕНИЕ JS ФАЙЛА:")
    print("-" * 70)
    try:
        response = requests.get(f"{BASE_URL}/app/", verify=False, timeout=5)
        html = response.text
        
        js_match = re.search(r'src="([^"]+\.js[^"]*)"', html)
        if not js_match:
            print("  ✗ JS файл не найден в HTML")
            return
        
        js_path = js_match.group(1)
        js_url = f"{BASE_URL}{js_path}"
        print(f"  JS файл: {js_path}")
        
        # Загружаем JS файл
        js_response = requests.get(js_url, verify=False, timeout=10)
        js_content = js_response.text
        
        print(f"  Размер: {len(js_content)} байт")
        
        # Ищем упоминания API URL
        print("\n2. ПОИСК API URL В КОДЕ:")
        print("-" * 70)
        
        # Ищем различные паттерны
        patterns = [
            (r'http://72\.56\.79\.153:8000', 'HTTP с портом 8000'),
            (r'http://localhost:8000', 'HTTP localhost:8000'),
            (r'https://72\.56\.79\.153/api', 'HTTPS /api'),
            (r'window\.location\.protocol', 'window.location.protocol'),
            (r'window\.location\.host', 'window.location.host'),
            (r'getApiUrl', 'getApiUrl функция'),
        ]
        
        found_patterns = []
        for pattern, desc in patterns:
            matches = re.findall(pattern, js_content)
            if matches:
                found_patterns.append((pattern, desc, len(matches)))
                print(f"  ✓ Найдено '{desc}': {len(matches)} вхождений")
            else:
                print(f"  ✗ Не найдено '{desc}'")
        
        # Проверяем, есть ли правильный код
        if 'window.location.protocol' in js_content and 'window.location.host' in js_content:
            print("\n  ✓ Код использует динамическое определение URL")
        else:
            print("\n  ✗ Код НЕ использует динамическое определение URL")
        
        # Ищем конкретные URL
        print("\n3. ПОИСК КОНКРЕТНЫХ URL:")
        print("-" * 70)
        url_patterns = [
            r'["\']http://[^"\']+["\']',
            r'["\']https://[^"\']+["\']',
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, js_content)
            api_urls = [m for m in matches if 'api' in m.lower() or '8000' in m or 'localhost' in m]
            if api_urls:
                print(f"  Найдены URL:")
                for url in api_urls[:5]:  # Показываем первые 5
                    print(f"    {url}")
        
        # Проверяем на сервере исходный файл
        print("\n4. ПРОВЕРКА ИСХОДНОГО ФАЙЛА НА СЕРВЕРЕ:")
        print("-" * 70)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("72.56.79.153", username="root", password="m8J@2_6whwza6U", timeout=30)
        
        try:
            success, api_ts_content, error = ssh_exec(ssh, "cat /root/shannon/template/src/services/api.ts | grep -A 15 'getApiUrl'")
            if 'getApiUrl' in api_ts_content:
                print("  ✓ Исходный файл содержит getApiUrl:")
                print(f"  {api_ts_content[:500]}")
            else:
                print("  ✗ Исходный файл НЕ содержит getApiUrl")
        finally:
            ssh.close()
        
        print("\n" + "="*70)
        print("РЕКОМЕНДАЦИИ")
        print("="*70)
        if 'window.location.protocol' not in js_content:
            print("⚠ JavaScript файл не содержит динамическое определение URL")
            print("  Нужно пересобрать фронтенд с исправленным api.ts")
        else:
            print("✓ JavaScript файл содержит правильный код")
            print("  Проблема может быть в кэше браузера")
            print("\nПопробуйте:")
            print("1. Очистить кэш браузера (Ctrl+Shift+Delete)")
            print("2. Открыть страницу в режиме инкогнито")
            print("3. Добавить ?v=2 к URL: https://72.56.79.153/app/?v=2")
        print("="*70)
        
    except Exception as e:
        print(f"✗ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()



