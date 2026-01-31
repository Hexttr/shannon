#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест логина с заголовками браузера
"""

import requests
from urllib3.exceptions import InsecureRequestWarning
import urllib3

urllib3.disable_warnings(InsecureRequestWarning)

SSH_HOST = "72.56.79.153"

def main():
    print("="*60)
    print("ТЕСТ ЛОГИНА С ЗАГОЛОВКАМИ БРАУЗЕРА")
    print("="*60)
    
    # Тест как браузер
    print("\n1. ТЕСТ КАК БРАУЗЕР:")
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
    print(f"  Заголовки запроса:")
    print(f"    Origin: {response.request.headers.get('Origin')}")
    print(f"    Content-Type: {response.request.headers.get('Content-Type')}")
    print(f"  Заголовки ответа:")
    for key, value in response.headers.items():
        if 'access-control' in key.lower() or 'content-type' in key.lower():
            print(f"    {key}: {value}")
    
    if response.status_code == 200:
        print(f"\n  ✅ Успешно!")
        print(f"  Ответ: {response.text[:200]}")
    else:
        print(f"\n  ❌ Ошибка {response.status_code}")
        print(f"  Ответ: {response.text[:500]}")
    
    # Тест с неправильным форматом (как может отправлять браузер)
    print("\n2. ТЕСТ С FORM-DATA:")
    response = requests.post(
        f"https://{SSH_HOST}/api/auth/login",
        data={"username": "admin", "password": "admin"},
        headers={
            "Origin": f"https://{SSH_HOST}",
            "Referer": f"https://{SSH_HOST}/",
        },
        verify=False,
        timeout=10
    )
    
    print(f"  Статус: {response.status_code}")
    if response.status_code != 200:
        print(f"  Ответ: {response.text[:300]}")

if __name__ == "__main__":
    main()

