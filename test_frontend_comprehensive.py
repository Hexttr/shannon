#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексное тестирование фронтенда
"""

import paramiko
import requests
import sys
from urllib.parse import urljoin

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
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

def test_http_request(url, description):
    """Тестирует HTTP запрос"""
    try:
        response = requests.get(url, verify=False, timeout=10, allow_redirects=True)
        status_ok = response.status_code == 200
        content_type = response.headers.get('Content-Type', '')
        
        print(f"  {description}")
        print(f"    URL: {url}")
        print(f"    Статус: {response.status_code} {'✓' if status_ok else '✗'}")
        print(f"    Content-Type: {content_type}")
        print(f"    Размер: {len(response.content)} байт")
        
        return status_ok, response
    except Exception as e:
        print(f"  {description}")
        print(f"    URL: {url}")
        print(f"    Ошибка: {str(e)} ✗")
        return False, None

def main():
    print("="*70)
    print("КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ ФРОНТЕНДА")
    print("="*70)
    
    results = {
        'passed': 0,
        'failed': 0,
        'warnings': 0
    }
    
    # 1. Тест главной страницы
    print("\n1. ТЕСТ ГЛАВНОЙ СТРАНИЦЫ (/app/):")
    print("-" * 70)
    success, response = test_http_request(f"{BASE_URL}/app/", "Главная страница")
    if success:
        results['passed'] += 1
        
        # Проверяем содержимое HTML
        html = response.text
        checks = {
            '<div id="root"></div>': 'Элемент #root найден',
            '<script type="module"': 'JavaScript модуль найден',
            '<link rel="stylesheet"': 'CSS файл найден',
            '/assets/': 'Пути к assets правильные',
        }
        
        for check, desc in checks.items():
            if check in html:
                print(f"    ✓ {desc}")
                results['passed'] += 1
            else:
                print(f"    ✗ {desc} - НЕ НАЙДЕНО")
                results['failed'] += 1
        
        # Извлекаем пути к JS и CSS
        import re
        js_match = re.search(r'src="([^"]+\.js)"', html)
        css_match = re.search(r'href="([^"]+\.css)"', html)
        
        if js_match:
            js_path = js_match.group(1)
            print(f"\n    Найден JS файл: {js_path}")
            if js_path.startswith('/assets/'):
                print(f"    ✓ Путь к JS правильный")
                results['passed'] += 1
            else:
                print(f"    ✗ Путь к JS неправильный (должен начинаться с /assets/)")
                results['failed'] += 1
        
        if css_match:
            css_path = css_match.group(1)
            print(f"    Найден CSS файл: {css_path}")
            if css_path.startswith('/assets/'):
                print(f"    ✓ Путь к CSS правильный")
                results['passed'] += 1
            else:
                print(f"    ✗ Путь к CSS неправильный (должен начинаться с /assets/)")
                results['failed'] += 1
    else:
        results['failed'] += 1
    
    # 2. Тест JavaScript файла
    print("\n2. ТЕСТ JAVASCRIPT ФАЙЛА:")
    print("-" * 70)
    if js_match:
        js_url = urljoin(BASE_URL, js_path)
        success, response = test_http_request(js_url, "JavaScript файл")
        if success:
            results['passed'] += 1
            content_type = response.headers.get('Content-Type', '')
            if 'javascript' in content_type.lower():
                print(f"    ✓ Content-Type правильный (application/javascript)")
                results['passed'] += 1
            else:
                print(f"    ✗ Content-Type неправильный: {content_type}")
                results['failed'] += 1
            
            # Проверяем, что это действительно JS код
            js_content = response.text[:200]
            if any(keyword in js_content for keyword in ['import', 'function', 'const', 'var', 'export']):
                print(f"    ✓ Файл содержит JavaScript код")
                results['passed'] += 1
            else:
                print(f"    ✗ Файл не содержит JavaScript код (возможно HTML)")
                print(f"    Первые символы: {js_content[:100]}")
                results['failed'] += 1
    
    # 3. Тест CSS файла
    print("\n3. ТЕСТ CSS ФАЙЛА:")
    print("-" * 70)
    if css_match:
        css_url = urljoin(BASE_URL, css_path)
        success, response = test_http_request(css_url, "CSS файл")
        if success:
            results['passed'] += 1
            content_type = response.headers.get('Content-Type', '')
            if 'css' in content_type.lower():
                print(f"    ✓ Content-Type правильный (text/css)")
                results['passed'] += 1
            else:
                print(f"    ✗ Content-Type неправильный: {content_type}")
                results['failed'] += 1
    
    # 4. Тест API endpoints
    print("\n4. ТЕСТ API ENDPOINTS:")
    print("-" * 70)
    api_endpoints = [
        ('/api/auth/login', 'POST', 'Логин endpoint'),
        ('/api/auth/me', 'GET', 'Текущий пользователь endpoint'),
    ]
    
    for endpoint, method, desc in api_endpoints:
        url = f"{BASE_URL}{endpoint}"
        try:
            if method == 'POST':
                response = requests.post(url, json={}, verify=False, timeout=5)
            else:
                response = requests.get(url, verify=False, timeout=5)
            
            # API должен отвечать (даже с ошибкой 401/422 - это нормально)
            if response.status_code in [200, 401, 422, 500]:
                print(f"    ✓ {desc}: {response.status_code}")
                results['passed'] += 1
            else:
                print(f"    ✗ {desc}: {response.status_code}")
                results['failed'] += 1
        except Exception as e:
            print(f"    ✗ {desc}: Ошибка - {str(e)}")
            results['failed'] += 1
    
    # 5. Тест React Router маршрутов
    print("\n5. ТЕСТ REACT ROUTER МАРШРУТОВ:")
    print("-" * 70)
    routes = ['/app/', '/app/home', '/app/home/services']
    
    for route in routes:
        url = f"{BASE_URL}{route}"
        success, response = test_http_request(url, f"Маршрут {route}")
        if success:
            # Все маршруты должны возвращать index.html для SPA
            if '<div id="root"></div>' in response.text:
                print(f"    ✓ Маршрут {route} возвращает SPA")
                results['passed'] += 1
            else:
                print(f"    ✗ Маршрут {route} не возвращает SPA")
                results['failed'] += 1
        else:
            results['failed'] += 1
    
    # 6. Проверка конфигурации на сервере
    print("\n6. ПРОВЕРКА КОНФИГУРАЦИИ НА СЕРВЕРЕ:")
    print("-" * 70)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Проверяем Nginx конфигурацию
        success, nginx_config, error = ssh_exec(ssh, "grep -A 3 'location /app' /etc/nginx/sites-available/pentest | head -5")
        if 'try_files' in nginx_config:
            print("    ✓ Nginx конфигурация для SPA правильная")
            results['passed'] += 1
        else:
            print("    ✗ Nginx конфигурация для SPA неправильная (нет try_files)")
            results['failed'] += 1
        
        # Проверяем наличие dist
        success2, dist_check, error2 = ssh_exec(ssh, "ls -d /root/shannon/template/dist 2>&1")
        if 'No such file' not in dist_check:
            print("    ✓ Директория dist существует")
            results['passed'] += 1
        else:
            print("    ✗ Директория dist не существует")
            results['failed'] += 1
        
        # Проверяем права доступа
        success3, perms_check, error3 = ssh_exec(ssh, "stat -c '%U:%G' /root/shannon/template/dist/index.html 2>&1")
        if 'www-data' in perms_check:
            print("    ✓ Права доступа правильные")
            results['passed'] += 1
        else:
            print(f"    ⚠ Права доступа: {perms_check.strip()}")
            results['warnings'] += 1
        
    finally:
        ssh.close()
    
    # Итоги
    print("\n" + "="*70)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*70)
    total = results['passed'] + results['failed']
    print(f"Пройдено: {results['passed']} ✓")
    print(f"Провалено: {results['failed']} ✗")
    print(f"Предупреждения: {results['warnings']} ⚠")
    print(f"Всего тестов: {total}")
    
    if results['failed'] == 0:
        print("\n✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    else:
        print(f"\n✗ НАЙДЕНО ПРОБЛЕМ: {results['failed']}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()



