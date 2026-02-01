#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from server_utils import ServerConnection

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

with ServerConnection() as conn:
    print("Проверка ошибок авторизации...")
    
    # Проверка последних ошибок
    output, error, code = conn.execute("tail -50 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'ERROR|Exception|auth|login' | tail -20")
    print(output)
    
    # Тест API
    print("\nТест /api/auth/login:")
    output, error, code = conn.execute("curl -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' 2>&1")
    print(output[-300:])


