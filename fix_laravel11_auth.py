#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление аутентификации для Laravel 11
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def fix_bootstrap_app(conn):
    """Исправляет bootstrap/app.php правильным способом для Laravel 11"""
    print("\n" + "="*60)
    print("🔧 Исправление bootstrap/app.php для Laravel 11...")
    print("="*60)
    
    # Правильная версия для Laravel 11
    correct_bootstrap = '''<?php

use Illuminate\\Foundation\\Application;
use Illuminate\\Foundation\\Configuration\\Exceptions;
use Illuminate\\Foundation\\Configuration\\Middleware;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware) {
        // EnsureFrontendRequestsAreStateful убран для API - используем токены без CSRF
        // Для API используем Bearer токены, CSRF не требуется

        $middleware->alias([
            'verified' => \\App\\Http\\Middleware\\EnsureEmailIsVerified::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions) {
        // Обработка неаутентифицированных запросов для API
        $exceptions->shouldRenderJsonWhen(function (\\Illuminate\\Http\\Request $request, \\Throwable $e) {
            return $request->expectsJson() || $request->is('api/*');
        });
    })->create();
'''
    
    file_path = "/root/shannon/backend-laravel/bootstrap/app.php"
    conn.execute(f"cat > {file_path} << 'EOFBOOTSTRAP'\n{correct_bootstrap}EOFBOOTSTRAP")
    
    # Проверяем синтаксис
    output, error, code = conn.execute(f"php -l {file_path} 2>&1")
    if code == 0:
        print("✅ Файл исправлен")
        return True
    else:
        print(f"❌ Ошибка: {error}")
        return False

def fix_authenticate_middleware(conn):
    """Исправляет Authenticate middleware"""
    print("\n" + "="*60)
    print("🔧 Исправление Authenticate middleware...")
    print("="*60)
    
    correct_middleware = '''<?php

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
        // Всегда возвращаем null - для API будет JSON, для веб тоже null
        return null;
    }
}
'''
    
    file_path = "/root/shannon/backend-laravel/app/Http/Middleware/Authenticate.php"
    conn.execute(f"cat > {file_path} << 'EOFMIDDLEWARE'\n{correct_middleware}EOFMIDDLEWARE")
    
    # Проверяем синтаксис
    output, error, code = conn.execute(f"php -l {file_path} 2>&1")
    if code == 0:
        print("✅ Middleware исправлен")
        return True
    else:
        print(f"❌ Ошибка: {error}")
        return False

def main():
    """Главная функция"""
    print("="*60)
    print("🔧 Исправление аутентификации для Laravel 11")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        if fix_bootstrap_app(conn) and fix_authenticate_middleware(conn):
            # Очищаем все кэши
            print("\n🧹 Очистка всех кэшей...")
            conn.execute("cd /root/shannon/backend-laravel && php artisan optimize:clear && php artisan config:clear")
            
            # Перезапускаем
            print("\n🔄 Перезапуск Laravel...")
            conn.execute("systemctl restart shannon-laravel")
            
            import time
            time.sleep(3)
            
            # Тестируем
            print("\n🔍 Тестирование API...")
            output, error, code = conn.execute("curl -s -w '\\nHTTP_CODE:%{http_code}' http://localhost:8000/api/pentests 2>&1")
            if output:
                if 'HTTP_CODE:401' in output:
                    print("✅ API работает! (401 - ожидаемо без авторизации)")
                    print("\n✅ Проблема решена!")
                elif 'HTTP_CODE:500' in output:
                    print("❌ Все еще 500 ошибка")
                    # Показываем последнюю ошибку
                    output2, error2, code2 = conn.execute("tail -n 50 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -A 20 'ERROR' | tail -n 30")
                    if output2:
                        print("\nПоследняя ошибка:")
                        print(output2)
                else:
                    print(f"⚠️  Статус: {output[-50:]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


