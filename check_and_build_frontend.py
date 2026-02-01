#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка и сборка фронтенда
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_frontend_source(conn):
    """Проверяет исходники фронтенда"""
    print("\n" + "="*60)
    print("🔍 Проверка исходников фронтенда...")
    print("="*60)
    
    template_path = "/root/shannon/template"
    
    # Проверяем существование
    output, error, code = conn.execute(f"test -d {template_path} && echo 'exists' || echo 'not-found'")
    if 'exists' in output:
        print(f"✅ Директория существует: {template_path}")
        
        # Проверяем package.json
        output2, error2, code2 = conn.execute(f"test -f {template_path}/package.json && echo 'exists' || echo 'not-found'")
        if 'exists' in output2:
            print(f"✅ package.json найден")
        else:
            print(f"❌ package.json не найден")
        
        # Проверяем dist
        output3, error3, code3 = conn.execute(f"test -d {template_path}/dist && echo 'exists' || echo 'not-found'")
        if 'exists' in output3:
            print(f"✅ dist существует")
            
            # Проверяем index.html
            output4, error4, code4 = conn.execute(f"test -f {template_path}/dist/index.html && echo 'exists' || echo 'not-found'")
            if 'exists' in output4:
                print(f"✅ index.html существует")
            else:
                print(f"❌ index.html не найден в dist")
        else:
            print(f"⚠️  dist не существует - нужно собрать")
    else:
        print(f"❌ Директория не существует: {template_path}")

def build_frontend(conn):
    """Собирает фронтенд"""
    print("\n" + "="*60)
    print("🔧 Сборка фронтенда...")
    print("="*60)
    
    template_path = "/root/shannon/template"
    
    # Проверяем наличие node_modules
    output, error, code = conn.execute(f"test -d {template_path}/node_modules && echo 'exists' || echo 'not-found'")
    if 'not-found' in output:
        print("📦 Установка зависимостей...")
        output2, error2, code2 = conn.execute(f"cd {template_path} && npm install 2>&1")
        if code2 == 0:
            print("✅ Зависимости установлены")
        else:
            print(f"❌ Ошибка установки зависимостей: {error2}")
            return False
    
    # Собираем фронтенд
    print("\n🔨 Сборка фронтенда...")
    output3, error3, code3 = conn.execute(f"cd {template_path} && npm run build 2>&1")
    
    if code3 == 0:
        print("✅ Фронтенд собран")
        if output3:
            # Показываем последние строки вывода
            lines = output3.split('\n')
            print("\n".join(lines[-10:]))
        return True
    else:
        print(f"❌ Ошибка сборки:")
        print(f"   {error3}")
        if output3:
            print(f"   {output3[-500:]}")
        return False

def verify_build(conn):
    """Проверяет результат сборки"""
    print("\n" + "="*60)
    print("🔍 Проверка результата сборки...")
    print("="*60)
    
    dist_path = "/root/shannon/template/dist"
    
    output, error, code = conn.execute(f"test -d {dist_path} && echo 'exists' || echo 'not-found'")
    if 'exists' in output:
        print(f"✅ Директория dist существует")
        
        # Проверяем index.html
        output2, error2, code2 = conn.execute(f"test -f {dist_path}/index.html && echo 'exists' || echo 'not-found'")
        if 'exists' in output2:
            print(f"✅ index.html существует")
            
            # Проверяем размер
            output3, error3, code3 = conn.execute(f"ls -lh {dist_path}/index.html | awk '{{print $5}}'")
            if output3:
                print(f"   Размер: {output3.strip()}")
            
            # Проверяем assets
            output4, error4, code4 = conn.execute(f"ls -d {dist_path}/assets 2>&1")
            if 'assets' in output4:
                print(f"✅ Директория assets существует")
            else:
                print(f"⚠️  Директория assets не найдена")
            
            return True
        else:
            print(f"❌ index.html не найден")
            return False
    else:
        print(f"❌ Директория dist не существует")
        return False

def main():
    """Главная функция"""
    print("="*60)
    print("🔧 Проверка и сборка фронтенда")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        check_frontend_source(conn)
        
        if build_frontend(conn):
            if verify_build(conn):
                # Перезагружаем Nginx
                print("\n🔄 Перезагрузка Nginx...")
                conn.execute("systemctl reload nginx")
                
                print("\n✅ Фронтенд собран и готов к работе!")
            else:
                print("\n⚠️  Сборка завершена, но проверка не прошла")
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


