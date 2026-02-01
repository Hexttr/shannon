#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка исправленных файлов на сервер
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def upload_file(conn, local_path, remote_path):
    """Загружает файл на сервер"""
    with open(local_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Экранируем специальные символы для heredoc
    content_escaped = content.replace('$', '\\$')
    
    conn.execute(f"cat > {remote_path} << 'EOFFILE'\n{content}EOFFILE")
    
    # Проверяем синтаксис PHP
    output, error, code = conn.execute(f"php -l {remote_path} 2>&1")
    return code == 0

def main():
    """Главная функция"""
    print("="*60)
    print("📤 Загрузка исправленных файлов")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        files_to_upload = [
            ("backend-laravel/bootstrap/app.php", "/root/shannon/backend-laravel/bootstrap/app.php"),
            ("backend-laravel/app/Http/Middleware/Authenticate.php", "/root/shannon/backend-laravel/app/Http/Middleware/Authenticate.php"),
        ]
        
        for local, remote in files_to_upload:
            print(f"\n📤 Загрузка {local}...")
            if upload_file(conn, local, remote):
                print(f"✅ {local} загружен")
            else:
                print(f"❌ Ошибка загрузки {local}")
        
        # Очищаем кэш и перезапускаем
        print("\n🧹 Очистка кэша...")
        conn.execute("cd /root/shannon/backend-laravel && php artisan optimize:clear")
        
        print("\n🔄 Перезапуск Laravel...")
        conn.execute("systemctl restart shannon-laravel")
        
        import time
        time.sleep(3)
        
        # Тестируем
        print("\n🔍 Тестирование API...")
        output, error, code = conn.execute("curl -s -w '\\nHTTP_CODE:%{http_code}' http://localhost:8000/api/pentests 2>&1")
        if output:
            if 'HTTP_CODE:401' in output:
                print("✅ API работает! (401 - ожидаемо)")
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


