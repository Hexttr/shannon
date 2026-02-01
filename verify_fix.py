#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка исправлений
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
    print("ПРОВЕРКА ИСПРАВЛЕНИЙ")
    print("="*70)
    
    # Получаем текущий JS файл
    print("\n1. ПОЛУЧЕНИЕ ТЕКУЩЕГО JS ФАЙЛА:")
    print("-" * 70)
    try:
        response = requests.get(f"{BASE_URL}/app/", verify=False, timeout=5)
        html = response.text
        
        js_match = re.search(r'src="([^"]+\.js[^"]*)"', html)
        if not js_match:
            print("  ✗ JS файл не найден")
            return
        
        js_path = js_match.group(1)
        js_url = f"{BASE_URL}{js_path}"
        print(f"  JS файл: {js_path}")
        
        # Загружаем JS файл
        js_response = requests.get(js_url, verify=False, timeout=10)
        js_content = js_response.text
        
        print(f"  Размер: {len(js_content)} байт")
        
        # Проверяем наличие исправлений
        print("\n2. ПРОВЕРКА ИСПРАВЛЕНИЙ В КОДЕ:")
        print("-" * 70)
        
        # Ищем response.data.data
        if 'response.data.data' in js_content or '.data.data' in js_content:
            print("  ✓ Найден response.data.data - исправление применено")
        else:
            print("  ⚠ response.data.data не найден (возможно минифицирован)")
        
        # Проверяем на старый формат
        if 'res.data' in js_content and 'res.data.data' not in js_content:
            # Проверяем контекст
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect("72.56.79.153", username="root", password="m8J@2_6whwza6U", timeout=30)
            
            try:
                # Получаем путь к JS файлу на сервере
                js_file_path = f"/root/shannon/template/dist{js_path}"
                success, grep_result, error = ssh_exec(ssh, f"grep -o 'res.data' {js_file_path} | head -5")
                if grep_result.strip():
                    print("  ⚠ Найден старый формат res.data")
                    print("  Возможно, нужно пересобрать фронтенд")
            finally:
                ssh.close()
        
        print("\n" + "="*70)
        print("РЕКОМЕНДАЦИИ")
        print("="*70)
        print("1. Обновите страницу с очисткой кэша (Ctrl+Shift+R)")
        print("2. Если ошибка сохраняется, проверьте консоль браузера (F12)")
        print("3. Убедитесь, что используется новый JS файл")
        print("="*70)
        
    except Exception as e:
        print(f"✗ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()



