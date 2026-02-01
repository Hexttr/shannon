#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная диагностика проблемы с открытием страницы
"""

import paramiko
import requests
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "https://72.56.79.153"

# Отключаем предупреждения о SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_all_possible_issues():
    """Проверка всех возможных проблем"""
    print("="*70)
    print("ФИНАЛЬНАЯ ДИАГНОСТИКА ПРОБЛЕМЫ")
    print("="*70)
    
    issues_found = []
    
    # 1. Проверка доступности страницы
    print("\n1. ПРОВЕРКА ДОСТУПНОСТИ:")
    print("-" * 70)
    try:
        response = requests.get(f"{BASE_URL}/app/", verify=False, timeout=10)
        if response.status_code == 200:
            print(f"  ✓ Страница доступна (200 OK)")
        else:
            print(f"  ✗ Страница недоступна: {response.status_code}")
            issues_found.append(f"HTTP статус {response.status_code}")
    except Exception as e:
        print(f"  ✗ Ошибка подключения: {str(e)}")
        issues_found.append(f"Ошибка подключения: {str(e)}")
    
    # 2. Проверка SSL сертификата
    print("\n2. ПРОВЕРКА SSL:")
    print("-" * 70)
    try:
        response = requests.get(f"{BASE_URL}/app/", verify=True, timeout=5)
        print(f"  ✓ SSL сертификат валиден")
    except requests.exceptions.SSLError:
        print(f"  ⚠ SSL сертификат невалиден (самоподписанный)")
        print(f"    Это нормально для тестового сервера")
    except Exception as e:
        print(f"  ⚠ Проблема с SSL: {str(e)}")
    
    # 3. Проверка редиректов
    print("\n3. ПРОВЕРКА РЕДИРЕКТОВ:")
    print("-" * 70)
    try:
        # Проверяем корневой путь
        response = requests.get(f"{BASE_URL}/", verify=False, timeout=5, allow_redirects=False)
        if response.status_code in [301, 302, 307, 308]:
            location = response.headers.get('Location', '')
            print(f"  ✓ Редирект с / на {location}")
        else:
            print(f"  ⚠ Нет редиректа с / (статус: {response.status_code})")
    except Exception as e:
        print(f"  ✗ Ошибка: {str(e)}")
    
    # 4. Проверка конфигурации Nginx
    print("\n4. ПРОВЕРКА NGINX:")
    print("-" * 70)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("72.56.79.153", username="root", password="m8J@2_6whwza6U", timeout=30)
    
    try:
        # Проверяем синтаксис
        stdin, stdout, stderr = ssh.exec_command("nginx -t 2>&1")
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8', errors='replace')
        
        if exit_status == 0:
            print(f"  ✓ Синтаксис Nginx правильный")
        else:
            print(f"  ✗ Ошибка синтаксиса Nginx:")
            print(f"    {output}")
            issues_found.append("Ошибка синтаксиса Nginx")
        
        # Проверяем конфигурацию для /app
        stdin, stdout, stderr = ssh.exec_command("grep -A 3 'location /app' /etc/nginx/sites-available/pentest")
        config = stdout.read().decode('utf-8', errors='replace')
        
        if 'try_files' in config:
            print(f"  ✓ Конфигурация для SPA правильная")
        else:
            print(f"  ✗ Конфигурация для SPA неправильная (нет try_files)")
            issues_found.append("Неправильная конфигурация Nginx для SPA")
        
        # Проверяем статус Nginx
        stdin, stdout, stderr = ssh.exec_command("systemctl is-active nginx")
        status = stdout.read().decode('utf-8', errors='replace').strip()
        
        if status == 'active':
            print(f"  ✓ Nginx работает")
        else:
            print(f"  ✗ Nginx не работает: {status}")
            issues_found.append(f"Nginx не работает: {status}")
        
    finally:
        ssh.close()
    
    # 5. Проверка файлов на сервере
    print("\n5. ПРОВЕРКА ФАЙЛОВ:")
    print("-" * 70)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("72.56.79.153", username="root", password="m8J@2_6whwza6U", timeout=30)
    
    try:
        # Проверяем index.html
        stdin, stdout, stderr = ssh.exec_command("test -f /root/shannon/template/dist/index.html && echo exists || echo not_found")
        result = stdout.read().decode('utf-8', errors='replace').strip()
        if result == 'exists':
            print(f"  ✓ index.html существует")
        else:
            print(f"  ✗ index.html не найден")
            issues_found.append("index.html не найден")
        
        # Проверяем JS файлы
        stdin, stdout, stderr = ssh.exec_command("ls /root/shannon/template/dist/assets/*.js 2>&1 | wc -l")
        js_count = stdout.read().decode('utf-8', errors='replace').strip()
        if js_count.isdigit() and int(js_count) > 0:
            print(f"  ✓ Найдено {js_count} JS файлов")
        else:
            print(f"  ✗ JS файлы не найдены")
            issues_found.append("JS файлы не найдены")
        
        # Проверяем права доступа
        stdin, stdout, stderr = ssh.exec_command("stat -c '%a %U:%G' /root/shannon/template/dist/index.html 2>&1")
        perms = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"  Права доступа: {perms}")
        
    finally:
        ssh.close()
    
    # Итоги
    print("\n" + "="*70)
    print("ИТОГИ ДИАГНОСТИКИ")
    print("="*70)
    
    if issues_found:
        print(f"\n✗ НАЙДЕНО ПРОБЛЕМ: {len(issues_found)}")
        for i, issue in enumerate(issues_found, 1):
            print(f"  {i}. {issue}")
    else:
        print("\n✓ Очевидных проблем не найдено")
        print("\nВозможные причины проблемы:")
        print("  1. Браузер блокирует самоподписанный SSL сертификат")
        print("  2. JavaScript код не выполняется из-за ошибки в консоли")
        print("  3. Проблема с CORS или другими заголовками")
        print("  4. Кэш браузера содержит старую версию")
        print("  5. Браузер блокирует загрузку ресурсов")
    
    print("\n" + "="*70)
    print("РЕКОМЕНДАЦИИ")
    print("="*70)
    print("1. Откройте страницу в режиме инкогнито (чтобы исключить кэш)")
    print("2. Примите самоподписанный SSL сертификат (если браузер спрашивает)")
    print("3. Откройте консоль разработчика (F12) и проверьте:")
    print("   - Вкладка Console: есть ли ошибки?")
    print("   - Вкладка Network: все ли файлы загружаются (статус 200)?")
    print("   - Вкладка Elements: есть ли элемент #root?")
    print("4. Попробуйте открыть страницу напрямую:")
    print(f"   {BASE_URL}/app/")
    print("5. Проверьте, что вы используете HTTPS, а не HTTP")
    print("="*70)

if __name__ == "__main__":
    check_all_possible_issues()



