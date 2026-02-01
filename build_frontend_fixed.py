#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка фронтенда с исправлением прав доступа
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def build_frontend(conn):
    """Собирает фронтенд"""
    print("\n" + "="*60)
    print("🔧 Сборка фронтенда...")
    print("="*60)
    
    template_path = "/root/shannon/template"
    
    # Исправляем права доступа к node_modules/.bin
    print("🔐 Исправление прав доступа...")
    conn.execute(f"chmod -R +x {template_path}/node_modules/.bin 2>&1 || true")
    
    # Собираем через npx (более надежно)
    print("\n🔨 Сборка фронтенда через npx...")
    output, error, code = conn.execute(f"cd {template_path} && npx vite build 2>&1")
    
    if code == 0:
        print("✅ Фронтенд собран")
        if output:
            # Показываем последние строки
            lines = output.split('\n')
            print("\n".join(lines[-15:]))
        return True
    else:
        print(f"❌ Ошибка сборки:")
        if error:
            print(f"   {error}")
        if output:
            print(f"   {output[-500:]}")
        return False

def verify_and_reload(conn):
    """Проверяет результат и перезагружает Nginx"""
    print("\n" + "="*60)
    print("🔍 Проверка результата...")
    print("="*60)
    
    dist_path = "/root/shannon/template/dist"
    
    output, error, code = conn.execute(f"test -f {dist_path}/index.html && echo 'exists' || echo 'not-found'")
    if 'exists' in output:
        print("✅ index.html создан")
        
        # Перезагружаем Nginx
        print("\n🔄 Перезагрузка Nginx...")
        conn.execute("systemctl reload nginx")
        
        print("\n✅ Готово! Фронтенд собран и Nginx перезагружен")
        return True
    else:
        print("❌ index.html не найден")
        return False

def main():
    """Главная функция"""
    print("="*60)
    print("🔧 Сборка фронтенда")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        if build_frontend(conn):
            verify_and_reload(conn)
        else:
            print("\n❌ Не удалось собрать фронтенд")
        
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


