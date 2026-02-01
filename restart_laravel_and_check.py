#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Перезапуск Laravel и проверка работы
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def restart_laravel(conn):
    """Перезапускает Laravel сервис"""
    print("\n" + "="*60)
    print("🔄 Перезапуск Laravel сервиса...")
    print("="*60)
    
    output, error, code = conn.execute("systemctl restart shannon-laravel")
    if code == 0:
        print("✅ Laravel сервис перезапущен")
        
        # Ждем немного для запуска
        import time
        time.sleep(3)
        
        # Проверяем статус
        output, error, code = conn.execute("systemctl status shannon-laravel --no-pager | head -10")
        if output:
            print("\n📊 Статус сервиса:")
            print(output)
        
        return True
    else:
        print(f"❌ Ошибка перезапуска: {error}")
        return False

def check_api(conn):
    """Проверяет доступность API"""
    print("\n" + "="*60)
    print("🔍 Проверка доступности API...")
    print("="*60)
    
    # Проверяем health check
    output, error, code = conn.execute("curl -s http://localhost:8000/up 2>&1")
    if output and ('ok' in output.lower() or 'up' in output.lower()):
        print("✅ API доступен")
        return True
    else:
        print(f"⚠️  API недоступен или отвечает неожиданно")
        print(f"   Ответ: {output[:200]}")
        return False

def check_user_exists(conn):
    """Проверяет наличие пользователя"""
    print("\n" + "="*60)
    print("🔍 Проверка пользователей в базе...")
    print("="*60)
    
    output, error, code = conn.execute("cd /root/shannon/backend-laravel && php artisan tinker --execute=\"echo App\\\\Models\\\\User::count();\" 2>&1")
    if output:
        try:
            count = int(output.strip())
            if count > 0:
                print(f"✅ Найдено пользователей: {count}")
                return True
            else:
                print("⚠️  Пользователей нет в базе")
                print("   Рекомендуется создать пользователя через seeder")
                return False
        except:
            print(f"⚠️  Не удалось проверить пользователей: {output}")
            return False
    else:
        print("⚠️  Не удалось проверить пользователей")
        return False

def main():
    """Главная функция"""
    print("="*60)
    print("🔄 Перезапуск Laravel и проверка")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        # Перезапуск
        if restart_laravel(conn):
            # Проверка API
            if check_api(conn):
                # Проверка пользователей
                check_user_exists(conn)
                
                print("\n" + "="*60)
                print("✅ Laravel перезапущен и работает")
                print("="*60)
            else:
                print("\n⚠️  API недоступен, проверьте логи")
        else:
            print("\n❌ Не удалось перезапустить Laravel")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


