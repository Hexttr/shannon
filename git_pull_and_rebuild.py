#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Обновление кода из git и пересборка фронтенда
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def git_pull_and_rebuild():
    """Обновляет код из git и пересобирает фронтенд"""
    print("Обновление кода из git и пересборка...")
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # Обновление из git
        print("\n[1] Обновление кода из git...")
        output, error, code = conn.execute("cd /root/shannon && git pull origin master 2>&1")
        print(output[-500:] if output else "Обновление завершено")
        
        # Пересборка фронтенда
        print("\n[2] Пересборка фронтенда...")
        output, error, code = conn.execute("cd /root/shannon/template && npm run build 2>&1")
        
        # Показываем последние строки вывода
        if output:
            lines = output.split('\n')
            print('\n'.join(lines[-50:]))
        
        if code == 0 or 'dist' in output.lower():
            print("\n[OK] Фронтенд успешно собран!")
            
            # Проверка dist
            output, error, code = conn.execute("ls -la /root/shannon/template/dist/ | head -10")
            print(f"\n[3] Результат сборки:\n{output}")
            
            # Проверка index.html
            output, error, code = conn.execute("test -f /root/shannon/template/dist/index.html && echo 'OK' || echo 'NOT FOUND'")
            print(f"\n[4] index.html: {output}")
            
            return True
        else:
            print("\n[ERROR] Ошибка сборки!")
            if error:
                print(f"Ошибки: {error[-500:]}")
            return False

if __name__ == "__main__":
    success = git_pull_and_rebuild()
    sys.exit(0 if success else 1)

