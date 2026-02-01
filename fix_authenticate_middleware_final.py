#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальное исправление Authenticate middleware
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_and_fix_middleware(conn):
    """Проверяет и исправляет middleware"""
    print("\n" + "="*60)
    print("🔧 Исправление Authenticate middleware...")
    print("="*60)
    
    file_path = "/root/shannon/backend-laravel/app/Http/Middleware/Authenticate.php"
    
    # Читаем текущий файл
    output, error, code = conn.execute(f"cat {file_path}")
    
    if output:
        print("Текущее содержимое файла:")
        print(output)
        
        # Проверяем, правильно ли обрабатываются API запросы
        if "if ($request->expectsJson() || $request->is('api/*'))" in output and "return null;" in output:
            # Проверяем порядок - return null должен быть ДО route('login')
            lines = output.split('\n')
            api_check_line = None
            return_null_line = None
            route_login_line = None
            
            for i, line in enumerate(lines):
                if "expectsJson() || $request->is('api/*')" in line:
                    api_check_line = i
                if "return null;" in line and api_check_line is not None:
                    return_null_line = i
                if "route('login')" in line:
                    route_login_line = i
            
            if api_check_line is not None and return_null_line is not None and route_login_line is not None:
                if return_null_line < route_login_line:
                    print("✅ Middleware правильно настроен")
                    return True
                else:
                    print("⚠️  Неправильный порядок - исправляю...")
        else:
            print("⚠️  Middleware не содержит правильной обработки API")
    
    # Исправляем файл
    print("\n📝 Запись исправленного файла...")
    correct_content = '''<?php

namespace App\\Http\\Middleware;

use Illuminate\\Auth\\Middleware\\Authenticate as Middleware;
use Illuminate\\Http\\Request;

class Authenticate extends Middleware
{
    /**
     * Get the path the user should be redirected to when they are not authenticated.
     */
    protected function redirectTo(Request $request): ?string
    {
        // Для API запросов всегда возвращаем null (будет JSON ответ)
        if ($request->expectsJson() || $request->is('api/*')) {
            return null;
        }

        // Для веб-запросов пытаемся редиректить на login (если маршрут существует)
        try {
            return route('login');
        } catch (\\Exception $e) {
            // Если маршрут login не существует, возвращаем null
            return null;
        }
    }
}
'''
    
    conn.execute(f"cat > {file_path} << 'EOFMIDDLEWARE'\n{correct_content}EOFMIDDLEWARE")
    
    # Проверяем синтаксис
    output2, error2, code2 = conn.execute(f"php -l {file_path} 2>&1")
    if code2 == 0:
        print("✅ Файл исправлен и синтаксис правильный")
        return True
    else:
        print(f"❌ Синтаксическая ошибка: {error2}")
        return False

def clear_all_caches(conn):
    """Очищает все кэши"""
    print("\n" + "="*60)
    print("🧹 Очистка всех кэшей...")
    print("="*60)
    
    commands = [
        "php artisan config:clear",
        "php artisan cache:clear",
        "php artisan route:clear",
        "php artisan view:clear",
        "php artisan optimize:clear",
    ]
    
    for cmd in commands:
        output, error, code = conn.execute(f"cd /root/shannon/backend-laravel && {cmd} 2>&1")
        if code == 0:
            print(f"✅ {cmd}")
        else:
            print(f"⚠️  {cmd}: {error}")

def main():
    """Главная функция"""
    print("="*60)
    print("🔧 Финальное исправление Authenticate middleware")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        if check_and_fix_middleware(conn):
            clear_all_caches(conn)
            
            # Перезапускаем Laravel
            print("\n🔄 Перезапуск Laravel...")
            conn.execute("systemctl restart shannon-laravel")
            
            import time
            time.sleep(3)
            
            # Тестируем API
            print("\n🔍 Тестирование API...")
            output, error, code = conn.execute("curl -s -w '\\nHTTP_CODE:%{http_code}' http://localhost:8000/api/pentests 2>&1")
            if output:
                if 'HTTP_CODE:401' in output:
                    print("✅ API работает! (401 - ожидаемо без авторизации)")
                elif 'HTTP_CODE:500' in output:
                    print("❌ Все еще 500 ошибка")
                else:
                    print(f"⚠️  Статус: {output[-30:]}")
            
            print("\n✅ Готово")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


