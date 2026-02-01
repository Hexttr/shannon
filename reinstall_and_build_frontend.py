#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Переустановка зависимостей и сборка фронтенда
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def reinstall_dependencies(conn):
    """Переустанавливает зависимости"""
    print("\n" + "="*60)
    print("🔧 Переустановка зависимостей...")
    print("="*60)
    
    template_path = "/root/shannon/template"
    
    # Удаляем node_modules и package-lock.json
    print("🗑️  Удаление старых зависимостей...")
    conn.execute(f"cd {template_path} && rm -rf node_modules package-lock.json 2>&1")
    
    # Устанавливаем заново
    print("\n📦 Установка зависимостей...")
    output, error, code = conn.execute(f"cd {template_path} && npm install 2>&1")
    
    if code == 0:
        print("✅ Зависимости установлены")
        if output:
            # Показываем последние строки
            lines = output.split('\n')
            print("\n".join(lines[-5:]))
        return True
    else:
        print(f"❌ Ошибка установки:")
        if error:
            print(f"   {error}")
        if output:
            print(f"   {output[-500:]}")
        return False

def build_frontend(conn):
    """Собирает фронтенд"""
    print("\n" + "="*60)
    print("🔨 Сборка фронтенда...")
    print("="*60)
    
    template_path = "/root/shannon/template"
    
    output, error, code = conn.execute(f"cd {template_path} && npm run build 2>&1")
    
    if code == 0:
        print("✅ Фронтенд собран")
        if output:
            lines = output.split('\n')
            print("\n".join(lines[-10:]))
        return True
    else:
        print(f"❌ Ошибка сборки:")
        if error:
            print(f"   {error}")
        if output:
            print(f"   {output[-500:]}")
        return False

def verify_and_reload(conn):
    """Проверяет и перезагружает Nginx"""
    print("\n" + "="*60)
    print("🔍 Проверка результата...")
    print("="*60)
    
    dist_path = "/root/shannon/template/dist"
    
    output, error, code = conn.execute(f"test -f {dist_path}/index.html && echo 'exists' || echo 'not-found'")
    if 'exists' in output:
        print("✅ index.html создан")
        
        # Проверяем размер
        output2, error2, code2 = conn.execute(f"ls -lh {dist_path}/index.html | awk '{{print $5}}'")
        if output2:
            print(f"   Размер: {output2.strip()}")
        
        # Перезагружаем Nginx
        print("\n🔄 Перезагрузка Nginx...")
        conn.execute("systemctl reload nginx")
        
        print("\n✅ Готово!")
        return True
    else:
        print("❌ index.html не найден")
        return False

def main():
    """Главная функция"""
    print("="*60)
    print("🔧 Переустановка зависимостей и сборка фронтенда")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        if reinstall_dependencies(conn):
            if build_frontend(conn):
                verify_and_reload(conn)
            else:
                print("\n❌ Не удалось собрать фронтенд")
        else:
            print("\n❌ Не удалось установить зависимости")
        
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


