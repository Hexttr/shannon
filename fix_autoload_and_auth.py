#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление автозагрузки и проверка Authenticate middleware
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_interface_file(conn):
    """Проверяет файл интерфейса"""
    print("\n" + "="*60)
    print("🔍 Проверка файла интерфейса...")
    print("="*60)
    
    file_path = "/root/shannon/backend-laravel/app/Services/Contracts/AiAnalysisServiceInterface.php"
    
    # Проверяем содержимое файла
    output, error, code = conn.execute(f"head -n 10 {file_path} 2>&1")
    if output:
        print("Начало файла:")
        print(output)
        
        # Проверяем namespace
        output2, error2, code2 = conn.execute(f"grep 'namespace' {file_path}")
        if output2:
            print(f"\nNamespace: {output2}")
        
        # Проверяем синтаксис
        output3, error3, code3 = conn.execute(f"php -l {file_path} 2>&1")
        if code3 == 0:
            print("✅ Синтаксис правильный")
        else:
            print(f"❌ Синтаксическая ошибка: {error3}")

def fix_autoload(conn):
    """Исправляет автозагрузку"""
    print("\n" + "="*60)
    print("🔧 Исправление автозагрузки...")
    print("="*60)
    
    # Удаляем старый autoload cache
    print("🗑️  Удаление старого кэша autoload...")
    conn.execute("cd /root/shannon/backend-laravel && rm -f bootstrap/cache/config.php bootstrap/cache/services.php 2>&1")
    
    # Обновляем autoload
    print("🔄 Обновление autoload...")
    output, error, code = conn.execute("cd /root/shannon/backend-laravel && composer dump-autoload -o 2>&1")
    if code == 0:
        print("✅ Autoload обновлен")
        if output:
            print(f"\n   {output[-200:]}")
    else:
        print(f"⚠️  Ошибка: {error}")
        if output:
            print(f"   {output[-200:]}")

def check_authenticate_middleware(conn):
    """Проверяет Authenticate middleware"""
    print("\n" + "="*60)
    print("🔍 Проверка Authenticate middleware...")
    print("="*60)
    
    file_path = "/root/shannon/backend-laravel/app/Http/Middleware/Authenticate.php"
    
    # Проверяем метод redirectTo
    output, error, code = conn.execute(f"grep -A 10 'redirectTo' {file_path}")
    if output:
        print("Метод redirectTo:")
        print(output)
        
        # Проверяем, есть ли исправление для API
        output2, error2, code2 = conn.execute(f"grep -q 'expectsJson\\|api\\*' {file_path} && echo 'fixed' || echo 'not-fixed'")
        if 'fixed' in output2:
            print("✅ Middleware исправлен для API")
        else:
            print("❌ Middleware не исправлен, нужно обновить")

def update_authenticate_middleware(conn):
    """Обновляет Authenticate middleware"""
    print("\n" + "="*60)
    print("🔧 Обновление Authenticate middleware...")
    print("="*60)
    
    file_path = "/root/shannon/backend-laravel/app/Http/Middleware/Authenticate.php"
    
    # Читаем текущий файл
    output, error, code = conn.execute(f"cat {file_path}")
    
    if output and 'return null;' not in output:
        # Заменяем метод redirectTo
        new_content = '''<?php

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
        
        # Записываем новый файл
        conn.execute(f"cat > {file_path} << 'EOFMIDDLEWARE'\n{new_content}EOFMIDDLEWARE")
        print("✅ Middleware обновлен")

def test_classes(conn):
    """Тестирует загрузку классов"""
    print("\n" + "="*60)
    print("🔍 Тестирование загрузки классов...")
    print("="*60)
    
    classes = [
        "App\\\\Services\\\\Contracts\\\\AiAnalysisServiceInterface",
        "App\\\\Services\\\\OllamaApiService",
        "App\\\\Services\\\\AiServiceFactory",
    ]
    
    for class_name in classes:
        output, error, code = conn.execute(f"cd /root/shannon/backend-laravel && php artisan tinker --execute=\"echo class_exists('{class_name}') ? 'OK' : 'NOT_FOUND';\" 2>&1")
        if output:
            if 'OK' in output:
                print(f"✅ {class_name}")
            else:
                print(f"❌ {class_name} - не найден")
                print(f"   {output}")

def main():
    """Главная функция"""
    print("="*60)
    print("🔧 Исправление автозагрузки и middleware")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        check_interface_file(conn)
        fix_autoload(conn)
        check_authenticate_middleware(conn)
        update_authenticate_middleware(conn)
        
        # Очищаем кэш
        print("\n🧹 Очистка кэша...")
        conn.execute("cd /root/shannon/backend-laravel && php artisan config:clear && php artisan cache:clear")
        
        # Тестируем классы
        test_classes(conn)
        
        # Перезапускаем Laravel
        print("\n🔄 Перезапуск Laravel...")
        conn.execute("systemctl restart shannon-laravel")
        
        import time
        time.sleep(3)
        
        print("\n✅ Готово")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


