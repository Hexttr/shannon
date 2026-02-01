#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка доступности приложения и предоставление ссылки
"""

import paramiko
import sys
import requests
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Отключаем предупреждения о самоподписанных сертификатах
urllib3.disable_warnings(InsecureRequestWarning)

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SSH_HOST = "72.56.79.153"

def main():
    print("="*60)
    print("ПРОВЕРКА ДОСТУПНОСТИ ПРИЛОЖЕНИЯ")
    print("="*60)
    
    # Проверка HTTPS
    print("\n1. ПРОВЕРКА HTTPS:")
    try:
        response = requests.get(f"https://{SSH_HOST}", verify=False, timeout=10)
        if response.status_code == 200:
            print(f"  ✅ HTTPS доступен: https://{SSH_HOST}")
            print(f"  Статус: {response.status_code}")
        else:
            print(f"  ⚠️  HTTPS ответил со статусом: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Ошибка HTTPS: {e}")
    
    # Проверка HTTP (должен редиректить)
    print("\n2. ПРОВЕРКА HTTP:")
    try:
        response = requests.get(f"http://{SSH_HOST}", allow_redirects=False, timeout=10)
        if response.status_code in [301, 302]:
            print(f"  ✅ HTTP редиректит на HTTPS")
            print(f"  Location: {response.headers.get('Location', 'N/A')}")
        else:
            print(f"  ⚠️  HTTP статус: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Ошибка HTTP: {e}")
    
    # Проверка API
    print("\n3. ПРОВЕРКА API:")
    try:
        response = requests.post(
            f"https://{SSH_HOST}/api/auth/login",
            json={"username": "admin", "password": "admin"},
            verify=False,
            timeout=10
        )
        if response.status_code == 200 and "token" in response.text:
            print(f"  ✅ API работает")
        else:
            print(f"  ⚠️  API статус: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Ошибка API: {e}")
    
    print("\n" + "="*60)
    print("ССЫЛКИ ДЛЯ ДОСТУПА")
    print("="*60)
    print(f"\n🌐 Основная ссылка (HTTPS):")
    print(f"   https://{SSH_HOST}")
    print(f"\n📱 Альтернативная ссылка (HTTP, редирект на HTTPS):")
    print(f"   http://{SSH_HOST}")
    print(f"\n🔐 Учетные данные для входа:")
    print(f"   Логин: admin")
    print(f"   Пароль: admin")
    print(f"\n⚠️  ВАЖНО:")
    print(f"   Браузер покажет предупреждение о безопасности из-за")
    print(f"   самоподписанного сертификата. Это нормально для IP-адресов.")
    print(f"   Нажмите 'Продолжить' или 'Advanced' -> 'Proceed to site'")
    print(f"\n💡 Для копирования ссылки:")
    print(f"   https://{SSH_HOST}")

if __name__ == "__main__":
    main()


