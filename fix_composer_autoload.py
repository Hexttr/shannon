#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление автозагрузки Composer для Contracts
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_composer_json(conn):
    """Проверяет composer.json"""
    print("\n" + "="*60)
    print("🔍 Проверка composer.json...")
    print("="*60)
    
    composer_file = "/root/shannon/backend-laravel/composer.json"
    
    # Проверяем autoload секцию
    output, error, code = conn.execute(f"grep -A 10 '\"autoload\"' {composer_file}")
    if output:
        print("Autoload конфигурация:")
        print(output)
        
        # Проверяем, есть ли App\\Services\\Contracts
        output2, error2, code2 = conn.execute(f"grep -q 'App\\\\Services\\\\Contracts' {composer_file} && echo 'found' || echo 'not-found'")
        if 'not-found' in output2:
            print("\n⚠️  Contracts не указан в autoload")
            print("   Но это не должно быть проблемой, так как PSR-4 должен работать")

def test_interface_directly(conn):
    """Тестирует интерфейс напрямую"""
    print("\n" + "="*60)
    print("🔍 Прямое тестирование интерфейса...")
    print("="*60)
    
    # Пробуем загрузить файл напрямую
    test_script = """
<?php
require __DIR__ . '/vendor/autoload.php';

use App\\Services\\Contracts\\AiAnalysisServiceInterface;

if (interface_exists('App\\Services\\Contracts\\AiAnalysisServiceInterface')) {
    echo 'OK';
} else {
    echo 'NOT_FOUND';
}
"""
    
    conn.execute(f"cd /root/shannon/backend-laravel && cat > /tmp/test_interface.php << 'EOFTEST'\n{test_script}EOFTEST")
    
    output, error, code = conn.execute("cd /root/shannon/backend-laravel && php /tmp/test_interface.php 2>&1")
    if output:
        if 'OK' in output:
            print("✅ Интерфейс загружается напрямую")
        else:
            print(f"❌ Интерфейс не загружается: {output}")

def check_file_structure(conn):
    """Проверяет структуру файлов"""
    print("\n" + "="*60)
    print("🔍 Проверка структуры файлов...")
    print("="*60)
    
    # Проверяем директорию Contracts
    output, error, code = conn.execute("ls -la /root/shannon/backend-laravel/app/Services/Contracts/ 2>&1")
    if output:
        print("Содержимое директории Contracts:")
        print(output)
    
    # Проверяем, что файл существует и читается
    file_path = "/root/shannon/backend-laravel/app/Services/Contracts/AiAnalysisServiceInterface.php"
    output2, error2, code2 = conn.execute(f"test -r {file_path} && echo 'readable' || echo 'not-readable'")
    if 'readable' in output2:
        print(f"✅ Файл читаемый")
    else:
        print(f"❌ Файл не читаемый")

def regenerate_autoload(conn):
    """Перегенерирует autoload"""
    print("\n" + "="*60)
    print("🔧 Перегенерация autoload...")
    print("="*60)
    
    # Удаляем все кэши
    print("🗑️  Удаление всех кэшей...")
    conn.execute("cd /root/shannon/backend-laravel && rm -rf bootstrap/cache/*.php vendor/composer/autoload_*.php 2>&1")
    
    # Регенерируем autoload
    print("🔄 Регенерация autoload...")
    output, error, code = conn.execute("cd /root/shannon/backend-laravel && composer dump-autoload --no-scripts 2>&1")
    
    if code == 0:
        print("✅ Autoload регенерирован")
        if output:
            # Показываем последние строки
            lines = output.split('\n')
            print("\n".join(lines[-10:]))
    else:
        print(f"⚠️  Ошибка: {error}")
        if output:
            print(f"   {output[-300:]}")

def main():
    """Главная функция"""
    print("="*60)
    print("🔧 Исправление автозагрузки Composer")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        check_composer_json(conn)
        check_file_structure(conn)
        test_interface_directly(conn)
        regenerate_autoload(conn)
        
        # Тестируем снова
        print("\n🔍 Повторное тестирование...")
        output, error, code = conn.execute("cd /root/shannon/backend-laravel && php artisan tinker --execute=\"echo interface_exists('App\\\\Services\\\\Contracts\\\\AiAnalysisServiceInterface') ? 'OK' : 'NOT_FOUND';\" 2>&1")
        if output:
            if 'OK' in output:
                print("✅ Интерфейс теперь загружается!")
            else:
                print(f"❌ Интерфейс все еще не загружается: {output}")
        
        # Очищаем кэш и перезапускаем
        print("\n🧹 Очистка кэша...")
        conn.execute("cd /root/shannon/backend-laravel && php artisan config:clear && php artisan cache:clear")
        
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


