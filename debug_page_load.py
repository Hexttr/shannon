#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отладка загрузки страницы - симуляция браузера
"""

import paramiko
import requests
import sys
from urllib.parse import urljoin
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

def simulate_browser_load():
    """Симуляция загрузки страницы браузером"""
    print("="*70)
    print("СИМУЛЯЦИЯ ЗАГРУЗКИ СТРАНИЦЫ БРАУЗЕРОМ")
    print("="*70)
    
    print("\n1. ЗАГРУЗКА ГЛАВНОЙ СТРАНИЦЫ (/app/):")
    print("-" * 70)
    
    try:
        # Симулируем запрос браузера
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(
            f"{BASE_URL}/app/",
            headers=headers,
            verify=False,
            timeout=10,
            allow_redirects=True
        )
        
        print(f"  Статус: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type', 'не указан')}")
        print(f"  Content-Length: {len(response.content)} байт")
        print(f"  Заголовки ответа:")
        for key, value in response.headers.items():
            if key.lower() in ['content-type', 'content-length', 'server', 'date', 'etag']:
                print(f"    {key}: {value}")
        
        html = response.text
        print(f"\n  Размер HTML: {len(html)} байт")
        print(f"  Первые 500 символов HTML:")
        print(f"  {html[:500]}")
        
        # Проверяем наличие критических элементов
        checks = {
            '<html': 'HTML тег',
            '<head': 'HEAD тег',
            '<body': 'BODY тег',
            '<div id="root">': 'Root элемент',
            '<script': 'Script теги',
            '<link': 'Link теги (CSS)',
        }
        
        print(f"\n  Проверка элементов HTML:")
        for check, desc in checks.items():
            if check in html:
                print(f"    ✓ {desc} найден")
            else:
                print(f"    ✗ {desc} НЕ НАЙДЕН!")
        
        # Извлекаем пути к ресурсам
        print(f"\n2. АНАЛИЗ РЕСУРСОВ:")
        print("-" * 70)
        
        js_files = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', html)
        css_files = re.findall(r'href=["\']([^"\']+\.css[^"\']*)["\']', html)
        
        print(f"  Найдено JS файлов: {len(js_files)}")
        for js_file in js_files:
            print(f"    - {js_file}")
        
        print(f"  Найдено CSS файлов: {len(css_files)}")
        for css_file in css_files:
            print(f"    - {css_file}")
        
        # Проверяем загрузку каждого ресурса
        print(f"\n3. ПРОВЕРКА ЗАГРУЗКИ РЕСУРСОВ:")
        print("-" * 70)
        
        for js_file in js_files:
            js_url = urljoin(BASE_URL, js_file)
            try:
                js_response = requests.get(js_url, verify=False, timeout=5, headers=headers)
                print(f"  {js_file}:")
                print(f"    Статус: {js_response.status_code}")
                print(f"    Content-Type: {js_response.headers.get('Content-Type', 'не указан')}")
                print(f"    Размер: {len(js_response.content)} байт")
                
                if js_response.status_code == 200:
                    content_type = js_response.headers.get('Content-Type', '').lower()
                    if 'javascript' in content_type:
                        print(f"    ✓ Правильный Content-Type")
                    else:
                        print(f"    ✗ Неправильный Content-Type: {content_type}")
                        print(f"    Первые 200 символов ответа:")
                        print(f"    {js_response.text[:200]}")
                else:
                    print(f"    ✗ Ошибка загрузки!")
                    print(f"    Ответ: {js_response.text[:200]}")
            except Exception as e:
                print(f"  {js_file}: ✗ Ошибка - {str(e)}")
        
        for css_file in css_files:
            css_url = urljoin(BASE_URL, css_file)
            try:
                css_response = requests.get(css_url, verify=False, timeout=5, headers=headers)
                print(f"  {css_file}:")
                print(f"    Статус: {css_response.status_code}")
                print(f"    Content-Type: {css_response.headers.get('Content-Type', 'не указан')}")
                print(f"    Размер: {len(css_response.content)} байт")
                
                if css_response.status_code == 200:
                    content_type = css_response.headers.get('Content-Type', '').lower()
                    if 'css' in content_type:
                        print(f"    ✓ Правильный Content-Type")
                    else:
                        print(f"    ✗ Неправильный Content-Type: {content_type}")
            except Exception as e:
                print(f"  {css_file}: ✗ Ошибка - {str(e)}")
        
        return html, js_files, css_files
        
    except Exception as e:
        print(f"  ✗ Ошибка при загрузке страницы: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, [], []

def check_server_logs():
    """Проверка логов сервера"""
    print("\n4. ПРОВЕРКА ЛОГОВ СЕРВЕРА:")
    print("-" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("72.56.79.153", username="root", password="m8J@2_6whwza6U", timeout=30)
    
    try:
        # Проверяем логи Nginx
        print("  Nginx error log (последние 10 строк):")
        success, output, error = ssh_exec(ssh, "tail -10 /var/log/nginx/error.log 2>&1")
        if output.strip():
            print(f"    {output}")
        else:
            print("    Нет ошибок")
        
        # Проверяем логи Laravel
        print("\n  Laravel log (последние 10 строк):")
        success2, output2, error2 = ssh_exec(ssh, "tail -10 /root/shannon/backend-laravel/storage/logs/laravel.log 2>&1")
        if output2.strip() and 'No such file' not in output2:
            print(f"    {output2}")
        else:
            print("    Нет ошибок или файл не найден")
        
        # Проверяем доступность backend
        print("\n  Проверка backend (порт 8000):")
        success3, output3, error3 = ssh_exec(ssh, "curl -s http://127.0.0.1:8000/api/auth/login -X POST -H 'Content-Type: application/json' -d '{}' | head -5")
        print(f"    Ответ: {output3[:200]}")
        
    finally:
        ssh.close()

def check_nginx_config():
    """Проверка конфигурации Nginx"""
    print("\n5. ПРОВЕРКА КОНФИГУРАЦИИ NGINX:")
    print("-" * 70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("72.56.79.153", username="root", password="m8J@2_6whwza6U", timeout=30)
    
    try:
        # Проверяем синтаксис
        success, output, error = ssh_exec(ssh, "nginx -t 2>&1")
        print(f"  Синтаксис Nginx: {'✓ OK' if success else '✗ ОШИБКА'}")
        if not success:
            print(f"    {error}")
        
        # Проверяем конфигурацию для /app
        success2, config, error2 = ssh_exec(ssh, "grep -A 5 'location /app' /etc/nginx/sites-available/pentest")
        print(f"\n  Конфигурация location /app:")
        print(f"    {config}")
        
        # Проверяем статус Nginx
        success3, status, error3 = ssh_exec(ssh, "systemctl status nginx --no-pager | head -10")
        print(f"\n  Статус Nginx:")
        print(f"    {status}")
        
    finally:
        ssh.close()

def main():
    # Симуляция браузера
    html, js_files, css_files = simulate_browser_load()
    
    # Проверка логов
    check_server_logs()
    
    # Проверка конфигурации
    check_nginx_config()
    
    # Итоги
    print("\n" + "="*70)
    print("ИТОГИ ОТЛАДКИ")
    print("="*70)
    
    if html and '<div id="root">' in html:
        print("✓ HTML страница загружается корректно")
    else:
        print("✗ Проблема с загрузкой HTML страницы")
    
    if js_files:
        print(f"✓ Найдено {len(js_files)} JS файлов")
    else:
        print("✗ JS файлы не найдены в HTML")
    
    if css_files:
        print(f"✓ Найдено {len(css_files)} CSS файлов")
    else:
        print("✗ CSS файлы не найдены в HTML")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()



