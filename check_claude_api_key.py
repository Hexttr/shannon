#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка Claude API ключа
"""

import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

def check_claude_key():
    """Проверяет Claude API ключ"""
    print("Проверка Claude API ключа...")
    
    with ServerConnection() as conn:
        if not conn.connected:
            print("[ERROR] Не удалось подключиться к серверу")
            return False
        
        # Проверка .env файла
        print("\n[1] Проверка CLAUDE_API_KEY в .env:")
        output, error, code = conn.execute("cd /root/shannon/backend-laravel && grep 'CLAUDE_API_KEY' .env")
        print(output)
        
        # Проверка ClaudeApiService
        print("\n[2] Проверка ClaudeApiService:")
        output, error, code = conn.execute("cat /root/shannon/backend-laravel/app/Services/ClaudeApiService.php | head -30")
        print(output)
        
        return True

if __name__ == "__main__":
    check_claude_key()


