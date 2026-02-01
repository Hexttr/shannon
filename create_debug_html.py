#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание отладочного HTML для проверки ошибок
"""

import sys
import os
import paramiko
from server_utils import SERVER_HOST, SERVER_USER, SERVER_PASSWORD, SERVER_PORT

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def create_debug_html():
    """Создает отладочный HTML"""
    print("Создание отладочного HTML...")
    
    debug_html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Debug - Frontend Check</title>
    <style>
        body { font-family: monospace; background: #000; color: #0f0; padding: 20px; }
        .error { color: #f00; }
        .success { color: #0f0; }
        .info { color: #0ff; }
        pre { background: #111; padding: 10px; border: 1px solid #333; }
    </style>
</head>
<body>
    <h1>Frontend Debug Check</h1>
    <div id="results"></div>
    <script>
        const results = document.getElementById('results');
        const log = (msg, type = 'info') => {
            const div = document.createElement('div');
            div.className = type;
            div.textContent = msg;
            results.appendChild(div);
            console.log(msg);
        };
        
        log('=== Начало проверки ===', 'info');
        
        // Проверка что root элемент существует
        const root = document.getElementById('root');
        if (root) {
            log('✓ Root элемент найден', 'success');
        } else {
            log('✗ Root элемент НЕ найден!', 'error');
        }
        
        // Проверка загрузки скриптов
        const scripts = document.querySelectorAll('script[type="module"]');
        log(`Найдено модульных скриптов: ${scripts.length}`, 'info');
        scripts.forEach((script, i) => {
            log(`  Скрипт ${i + 1}: ${script.src}`, 'info');
        });
        
        // Проверка загрузки стилей
        const styles = document.querySelectorAll('link[rel="stylesheet"]');
        log(`Найдено стилей: ${styles.length}`, 'info');
        styles.forEach((style, i) => {
            log(`  Стиль ${i + 1}: ${style.href}`, 'info');
        });
        
        // Проверка доступности API
        fetch('/api/auth/me', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            log(`API /api/auth/me: ${response.status} ${response.statusText}`, response.ok ? 'success' : 'error');
            return response.json();
        })
        .catch(error => {
            log(`API /api/auth/me: Ошибка - ${error.message}`, 'error');
        });
        
        // Проверка localStorage
        try {
            const token = localStorage.getItem('auth_token');
            log(`localStorage auth_token: ${token ? 'найден' : 'не найден'}`, token ? 'success' : 'info');
        } catch (e) {
            log(`localStorage недоступен: ${e.message}`, 'error');
        }
        
        // Проверка window.__DEBUG__
        if (window.__DEBUG__) {
            log('✓ window.__DEBUG__ доступен', 'success');
        } else {
            log('✗ window.__DEBUG__ НЕ доступен', 'error');
        }
        
        log('=== Проверка завершена ===', 'info');
        log('Откройте консоль браузера (F12) для подробностей', 'info');
    </script>
</body>
</html>"""
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    try:
        sftp = ssh.open_sftp()
        with sftp.file("/root/shannon/template/dist/debug.html", 'w') as f:
            f.write(debug_html)
        sftp.close()
        
        print("[OK] Отладочный HTML создан: https://72.56.79.153/debug.html")
        print("\nОткройте этот URL в браузере для диагностики")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    create_debug_html()


