#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная проверка фронтенда
"""

import sys
import os
import paramiko
from server_utils import SERVER_HOST, SERVER_USER, SERVER_PASSWORD, SERVER_PORT

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def final_check():
    """Финальная проверка фронтенда"""
    print("Финальная проверка фронтенда...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    try:
        # Проверка что все файлы на месте
        print("\n[1] Проверка структуры dist:")
        stdin, stdout, stderr = ssh.exec_command("ls -laR /root/shannon/template/dist/")
        output = stdout.read().decode('utf-8')
        print(output[:1000])
        
        # Проверка содержимого JS файла (первые строки)
        print("\n[2] Проверка JS файла (первые строки):")
        stdin, stdout, stderr = ssh.exec_command("head -5 /root/shannon/template/dist/assets/*.js | head -10")
        output = stdout.read().decode('utf-8')
        print(output)
        
        # Проверка что нет синтаксических ошибок в JS
        print("\n[3] Проверка синтаксиса JS файла:")
        stdin, stdout, stderr = ssh.exec_command("node -c /root/shannon/template/dist/assets/*.js 2>&1 | head -5")
        output = stdout.read().decode('utf-8')
        if output.strip():
            print(f"Ошибки: {output}")
        else:
            print("[OK] Синтаксис JS файла корректен")
        
        # Создание тестового HTML для проверки
        print("\n[4] Создание тестового HTML для проверки:")
        test_html = """<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
</head>
<body>
    <h1>Frontend Test</h1>
    <div id="test"></div>
    <script>
        console.log('Test script loaded');
        document.getElementById('test').innerHTML = 'JavaScript работает!';
    </script>
</body>
</html>"""
        
        stdin, stdout, stderr = ssh.exec_command("echo '" + test_html.replace("'", "'\"'\"'") + "' > /root/shannon/template/dist/test.html")
        stdout.read()
        
        print("\n[5] Проверка доступности через Nginx:")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost/test.html | head -10")
        output = stdout.read().decode('utf-8')
        print(output)
        
        # Проверка что index.html доступен
        print("\n[6] Проверка доступности index.html:")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost/ | head -15")
        output = stdout.read().decode('utf-8')
        print(output)
        
        # Проверка что assets доступны
        print("\n[7] Проверка доступности assets:")
        stdin, stdout, stderr = ssh.exec_command("ls /root/shannon/template/dist/assets/*.js | head -1 | xargs -I {} basename {}")
        js_file = stdout.read().decode('utf-8').strip()
        if js_file:
            stdin, stdout, stderr = ssh.exec_command(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost/assets/{js_file}")
            http_code = stdout.read().decode('utf-8').strip()
            print(f"JS файл {js_file}: HTTP {http_code}")
        
        print("\n[OK] Финальная проверка завершена!")
        print("\nФронтенд должен быть доступен по адресу: https://72.56.79.153")
        print("Если видите темный экран, откройте консоль браузера (F12) и проверьте ошибки")
        
        return True
        
    finally:
        ssh.close()

if __name__ == "__main__":
    final_check()


