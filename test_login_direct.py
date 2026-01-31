#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Прямой тест логина для проверки формата ответа
"""

import requests
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import json

urllib3.disable_warnings(InsecureRequestWarning)

SSH_HOST = "72.56.79.153"

def main():
    print("="*60)
    print("ТЕСТ ЛОГИНА")
    print("="*60)
    
    # Тест с правильными данными
    print("\n1. ТЕСТ С ПРАВИЛЬНЫМИ ДАННЫМИ:")
    response = requests.post(
        f"https://{SSH_HOST}/api/auth/login",
        json={"username": "admin", "password": "admin"},
        headers={
            "Content-Type": "application/json",
            "Origin": f"https://{SSH_HOST}",
            "Accept": "application/json",
        },
        verify=False,
        timeout=10
    )
    
    print(f"  Статус: {response.status_code}")
    print(f"  Заголовки:")
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
            print(f"    Полный ответ: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}")
        except:
            print(f"  Ответ (не JSON): {response.text[:300]}")
    else:
        print(f"\n  [ERROR] Ошибка:")
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
    if response.status_code != 200:
        try:
            data = response.json()
            print(f"  Формат ошибки: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}")
        except:
            print(f"  Ответ (не JSON): {response.text[:300]}")

if __name__ == "__main__":
    main()

