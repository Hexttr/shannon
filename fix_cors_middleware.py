#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление CORS middleware в Laravel 11
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def fix_cors_middleware():
    """Исправляет регистрацию CORS middleware в Laravel 11"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔧 Исправление CORS middleware...")
        print("="*60)
        
        # Читаем текущий bootstrap/app.php
        output, _, _ = conn.execute('cat /root/shannon/backend-laravel/bootstrap/app.php')
        print("\nТекущий bootstrap/app.php:")
        print(output)
        
        # Проверяем, есть ли HandleCors в middleware
        if 'HandleCors' not in output:
            print("\n⚠️  HandleCors middleware не найден в bootstrap/app.php")
            print("Добавляем...")
            
            # Создаем исправленную версию
            fixed_content = '''<?php

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
        // CORS middleware должен быть первым
        $middleware->priority([
            \\Illuminate\\Http\\Middleware\\HandleCors::class,
        ]);
        
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
            
            # Сохраняем исправленную версию
            conn.execute(f'cat > /tmp/bootstrap_app_fixed.php << \'BOOTSTRAP_EOF\'\n{fixed_content}\nBOOTSTRAP_EOF')
            conn.execute('cp /tmp/bootstrap_app_fixed.php /root/shannon/backend-laravel/bootstrap/app.php')
            print("✅ bootstrap/app.php обновлен")
        else:
            print("\n✅ HandleCors middleware уже есть в bootstrap/app.php")
        
        # Проверяем конфигурацию CORS
        print("\nПроверка конфигурации CORS:")
        output, _, _ = conn.execute('cat /root/shannon/backend-laravel/config/cors.php')
        print(output)
        
        # Перезапускаем Laravel сервис
        print("\nПерезапуск Laravel сервиса...")
        output, _, _ = conn.execute('systemctl restart shannon-laravel.service')
        output, _, _ = conn.execute('sleep 2 && systemctl status shannon-laravel.service --no-pager | head -10')
        print(output)
        
        # Тестируем CORS
        print("\nТестирование CORS...")
        curl_cmd = 'curl -s -k -X OPTIONS https://72.56.79.153/api/auth/login -H "Origin: https://72.56.79.153" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: content-type" -i 2>&1 | head -20'
        output, _, _ = conn.execute(curl_cmd)
        print(output)
        
        if 'Access-Control-Allow-Origin' in output:
            print("\n✅ CORS заголовки присутствуют!")
        else:
            print("\n⚠️  CORS заголовки не найдены в ответе")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_cors_middleware()

