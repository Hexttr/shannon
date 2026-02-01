#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка исправленного Reports.tsx на сервер
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def upload_reports_file(conn):
    """Загружает исправленный Reports.tsx"""
    print("\n" + "="*60)
    print("📤 Загрузка исправленного Reports.tsx...")
    print("="*60)
    
    local_file = "template/src/pages/Reports.tsx"
    remote_file = "/root/shannon/template/src/pages/Reports.tsx"
    
    # Читаем локальный файл
    with open(local_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Загружаем на сервер
    conn.execute(f"cat > {remote_file} << 'EOFREPORTS'\n{content}EOFREPORTS")
    
    # Проверяем синтаксис TypeScript
    print("\n🔍 Проверка синтаксиса...")
    output, error, code = conn.execute(f"cd /root/shannon/template && npx tsc --noEmit src/pages/Reports.tsx 2>&1 | head -20")
    if output:
        if 'error' in output.lower():
            print("⚠️  Есть ошибки TypeScript:")
            print(output[:500])
        else:
            print("✅ Синтаксис правильный")
    
    print("✅ Файл загружен")
    return True

def build_frontend(conn):
    """Собирает фронтенд"""
    print("\n" + "="*60)
    print("🔨 Сборка фронтенда...")
    print("="*60)
    
    template_path = "/root/shannon/template"
    
    output, error, code = conn.execute(f"cd {template_path} && npm run build 2>&1")
    
    if code == 0:
        print("✅ Фронтенд собран успешно")
        if output:
            lines = output.split('\n')
            print("\n".join(lines[-10:]))
        return True
    else:
        print(f"❌ Ошибка сборки:")
        if output:
            # Показываем только ошибки
            lines = output.split('\n')
            error_lines = [line for line in lines if 'error' in line.lower() or 'ERROR' in line]
            if error_lines:
                print("\n".join(error_lines[:20]))
            else:
                print(output[-500:])
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
    print("📤 Загрузка и сборка фронтенда")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        if upload_reports_file(conn):
            if build_frontend(conn):
                verify_and_reload(conn)
            else:
                print("\n❌ Не удалось собрать фронтенд")
        else:
            print("\n❌ Не удалось загрузить файл")
        
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


