#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование функциональности приложения
"""

import paramiko
import requests
import sys
import json

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "https://72.56.79.153"

# Отключаем предупреждения о SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_api_login():
    """Тест API логина"""
    print("\n1. ТЕСТ API ЛОГИНА:")
    print("-" * 70)
    
    url = f"{BASE_URL}/api/auth/login"
    
    # Тест с правильными данными
    try:
        response = requests.post(
            url,
            json={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            verify=False,
            timeout=5
        )
        
        print(f"  Запрос: POST {url}")
        print(f"  Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'token' in data and 'user' in data:
                print(f"  ✓ Логин успешен")
                print(f"    Токен получен: {'да' if data.get('token') else 'нет'}")
                print(f"    Пользователь: {data.get('user', {}).get('username', 'не найден')}")
                return True, data.get('token')
            else:
                print(f"  ✗ Неверный формат ответа")
                print(f"    Ответ: {data}")
                return False, None
        else:
            print(f"  ✗ Ошибка логина: {response.status_code}")
            try:
                error_data = response.json()
                print(f"    Ошибка: {error_data}")
            except:
                print(f"    Ответ: {response.text[:200]}")
            return False, None
    except Exception as e:
        print(f"  ✗ Исключение: {str(e)}")
        return False, None

def test_api_with_token(token):
    """Тест API с токеном"""
    print("\n2. ТЕСТ API С ТОКЕНОМ:")
    print("-" * 70)
    
    if not token:
        print("  ⚠ Токен не получен, пропускаем тест")
        return False
    
    url = f"{BASE_URL}/api/auth/me"
    
    try:
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            },
            verify=False,
            timeout=5
        )
        
        print(f"  Запрос: GET {url}")
        print(f"  Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Получены данные пользователя")
            print(f"    Пользователь: {data.get('username', 'не найден')}")
            print(f"    Email: {data.get('email', 'не найден')}")
            return True
        else:
            print(f"  ✗ Ошибка получения данных: {response.status_code}")
            try:
                error_data = response.json()
                print(f"    Ошибка: {error_data}")
            except:
                print(f"    Ответ: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Исключение: {str(e)}")
        return False

def test_frontend_resources():
    """Тест загрузки ресурсов фронтенда"""
    print("\n3. ТЕСТ ЗАГРУЗКИ РЕСУРСОВ:")
    print("-" * 70)
    
    # Получаем index.html
    try:
        response = requests.get(f"{BASE_URL}/app/", verify=False, timeout=5)
        html = response.text
        
        # Извлекаем пути к ресурсам
        import re
        js_files = re.findall(r'src="([^"]+\.js[^"]*)"', html)
        css_files = re.findall(r'href="([^"]+\.css[^"]*)"', html)
        
        print(f"  Найдено JS файлов: {len(js_files)}")
        print(f"  Найдено CSS файлов: {len(css_files)}")
        
        # Проверяем каждый JS файл
        for js_file in js_files:
            js_url = f"{BASE_URL}{js_file}"
            try:
                js_response = requests.get(js_url, verify=False, timeout=5)
                if js_response.status_code == 200:
                    content_type = js_response.headers.get('Content-Type', '')
                    if 'javascript' in content_type.lower():
                        print(f"    ✓ {js_file} - правильный Content-Type")
                    else:
                        print(f"    ✗ {js_file} - неправильный Content-Type: {content_type}")
                else:
                    print(f"    ✗ {js_file} - статус {js_response.status_code}")
            except Exception as e:
                print(f"    ✗ {js_file} - ошибка: {str(e)}")
        
        # Проверяем каждый CSS файл
        for css_file in css_files:
            css_url = f"{BASE_URL}{css_file}"
            try:
                css_response = requests.get(css_url, verify=False, timeout=5)
                if css_response.status_code == 200:
                    content_type = css_response.headers.get('Content-Type', '')
                    if 'css' in content_type.lower():
                        print(f"    ✓ {css_file} - правильный Content-Type")
                    else:
                        print(f"    ✗ {css_file} - неправильный Content-Type: {content_type}")
                else:
                    print(f"    ✗ {css_file} - статус {css_response.status_code}")
            except Exception as e:
                print(f"    ✗ {css_file} - ошибка: {str(e)}")
        
        return True
    except Exception as e:
        print(f"  ✗ Ошибка: {str(e)}")
        return False

def test_spa_routing():
    """Тест SPA маршрутизации"""
    print("\n4. ТЕСТ SPA МАРШРУТИЗАЦИИ:")
    print("-" * 70)
    
    routes = [
        '/app/',
        '/app/home',
        '/app/home/services',
        '/app/home/pentests',
        '/app/home/reports',
    ]
    
    all_ok = True
    for route in routes:
        url = f"{BASE_URL}{route}"
        try:
            response = requests.get(url, verify=False, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                if '<div id="root"></div>' in response.text:
                    print(f"    ✓ {route} - возвращает SPA")
                else:
                    print(f"    ✗ {route} - не возвращает SPA")
                    all_ok = False
            else:
                print(f"    ✗ {route} - статус {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"    ✗ {route} - ошибка: {str(e)}")
            all_ok = False
    
    return all_ok

def main():
    print("="*70)
    print("ТЕСТИРОВАНИЕ ФУНКЦИОНАЛЬНОСТИ ПРИЛОЖЕНИЯ")
    print("="*70)
    
    results = {
        'passed': 0,
        'failed': 0
    }
    
    # Тест логина
    login_ok, token = test_api_login()
    if login_ok:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Тест API с токеном
    if token:
        me_ok = test_api_with_token(token)
        if me_ok:
            results['passed'] += 1
        else:
            results['failed'] += 1
    
    # Тест ресурсов
    resources_ok = test_frontend_resources()
    if resources_ok:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Тест маршрутизации
    routing_ok = test_spa_routing()
    if routing_ok:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Итоги
    print("\n" + "="*70)
    print("ИТОГИ ФУНКЦИОНАЛЬНОГО ТЕСТИРОВАНИЯ")
    print("="*70)
    total = results['passed'] + results['failed']
    print(f"Пройдено: {results['passed']} ✓")
    print(f"Провалено: {results['failed']} ✗")
    print(f"Всего тестов: {total}")
    
    if results['failed'] == 0:
        print("\n✓ ВСЕ ФУНКЦИОНАЛЬНЫЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("\nПриложение готово к использованию.")
    else:
        print(f"\n✗ НАЙДЕНО ПРОБЛЕМ: {results['failed']}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()


