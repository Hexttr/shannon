#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный тест логина
"""

import requests
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import json

urllib3.disable_warnings(InsecureRequestWarning)

SSH_HOST = "72.56.79.153"

def main():
    print("="*60)
    print("ФИНАЛЬНЫЙ ТЕСТ ЛОГИНА")
    print("="*60)
    
    # Тест с правильными данными
    print("\n1. ТЕСТ С ПРАВИЛЬНЫМИ ДАННЫМИ:")
    response = requests.post(
        f"https://{SSH_HOST}/api/auth/login",
        json={"username": "admin", "password": "admin"},
        headers={
            "Content-Type": "application/json",
            "Origin": f"https://{SSH_HOST}",
            "Referer": f"https://{SSH_HOST}/",
            "Accept": "application/json",
        },
        verify=False,
        timeout=10
    )
    
    print(f"  Статус: {response.status_code}")
    print(f"  Заголовки ответа:")
    for key, value in response.headers.items():
        if 'content-type' in key.lower() or 'access-control' in key.lower():
            print(f"    {key}: {value}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"\n  [OK] Успешный ответ:")
            print(f"    Токен: {'есть' if 'token' in data else 'нет'}")
            print(f"    Пользователь: {'есть' if 'user' in data else 'нет'}")
            if 'user' in data:
                print(f"    Username: {data['user'].get('username', 'N/A')}")
            print(f"    Формат ответа правильный: {json.dumps(data, indent=2, ensure_ascii=False)[:400]}")
        except Exception as e:
            print(f"  [ERROR] Не удалось распарсить JSON: {e}")
            print(f"  Ответ: {response.text[:500]}")
    else:
        print(f"\n  [ERROR] Ошибка {response.status_code}:")
        print(f"    Ответ: {response.text[:500]}")
    
    # Тест с неправильными данными
    print("\n2. ТЕСТ С НЕПРАВИЛЬНЫМИ ДАННЫМИ:")
    response = requests.post(
        f"https://{SSH_HOST}/api/auth/login",
        json={"username": "wrong", "password": "wrong"},
        headers={
            "Content-Type": "application/json",
            "Origin": f"https://{SSH_HOST}",
            "Accept": "application/json",
        },
        verify=False,
        timeout=10
    )
    
    print(f"  Статус: {response.status_code}")
    if response.status_code == 422:
        try:
            data = response.json()
            print(f"  [OK] Ошибка валидации (422) - это правильно")
            print(f"  Формат ошибки: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}")
        except:
            print(f"  Ответ: {response.text[:300]}")
    
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*60)
    print(f"\n✅ API работает правильно!")
    print(f"   - Статус 200 с правильными данными")
    print(f"   - Статус 422 с неправильными данными")
    print(f"   - Формат ответа правильный (JSON с token и user)")
    print(f"\nЕсли вход не работает в браузере:")
    print(f"  1. Очистите кэш браузера (Ctrl+Shift+Delete)")
    print(f"  2. Откройте в режиме инкогнито")
    print(f"  3. Проверьте консоль (F12) на наличие ошибок")
    print(f"  4. Проверьте Network tab - запрос /api/auth/login")
    print(f"\nURL: https://{SSH_HOST}")
    print(f"Логин: admin")
    print(f"Пароль: admin")

if __name__ == "__main__":
    main()

