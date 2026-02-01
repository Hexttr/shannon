#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка конфигурации Nginx для фронтенда
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_nginx_config(conn):
    """Проверяет конфигурацию Nginx"""
    print("\n" + "="*60)
    print("🔍 Проверка конфигурации Nginx...")
    print("="*60)
    
    # Ищем конфигурационный файл
    config_files = [
        "/etc/nginx/sites-available/shannon",
        "/etc/nginx/sites-enabled/shannon",
        "/etc/nginx/conf.d/shannon.conf",
        "/root/shannon/nginx_shannon.conf",
    ]
    
    config_content = None
    config_path = None
    
    for config_file in config_files:
        output, error, code = conn.execute(f"test -f {config_file} && echo 'exists' || echo 'not-found'")
        if 'exists' in output:
            print(f"\n📄 Найден файл: {config_file}")
            output2, error2, code2 = conn.execute(f"cat {config_file}")
            if output2:
                config_content = output2
                config_path = config_file
                print("Содержимое:")
                print(config_content)
                break
    
    return config_path, config_content

def check_frontend_files(conn):
    """Проверяет файлы фронтенда"""
    print("\n" + "="*60)
    print("🔍 Проверка файлов фронтенда...")
    print("="*60)
    
    dist_path = "/root/shannon/template/dist"
    
    # Проверяем существование
    output, error, code = conn.execute(f"test -d {dist_path} && echo 'exists' || echo 'not-found'")
    if 'exists' in output:
        print(f"✅ Директория существует: {dist_path}")
        
        # Проверяем index.html
        output2, error2, code2 = conn.execute(f"test -f {dist_path}/index.html && echo 'exists' || echo 'not-found'")
        if 'exists' in output2:
            print(f"✅ index.html существует")
            
            # Проверяем размер
            output3, error3, code3 = conn.execute(f"ls -lh {dist_path}/index.html | awk '{{print $5}}'")
            if output3:
                print(f"   Размер: {output3.strip()}")
        else:
            print(f"❌ index.html не найден")
    else:
        print(f"❌ Директория не существует: {dist_path}")

def main():
    """Главная функция"""
    print("="*60)
    print("🔍 Проверка конфигурации Nginx")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        check_frontend_files(conn)
        config_path, config_content = check_nginx_config(conn)
        
        if config_content and '@fallback' in config_content:
            print("\n⚠️  Найден @fallback в конфигурации - это может быть причиной цикла")
        
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


