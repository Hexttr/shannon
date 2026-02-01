#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка исправленных файлов Reports.tsx и Home.tsx на сервер
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
    
    conn.execute(f"cat > {remote_path} << 'EOFFILE'\n{content}EOFFILE")
    return True

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
            ("template/src/pages/Reports.tsx", "/root/shannon/template/src/pages/Reports.tsx"),
            ("template/src/pages/Home.tsx", "/root/shannon/template/src/pages/Home.tsx"),
        ]
        
        for local, remote in files_to_upload:
            print(f"\n📤 Загрузка {local}...")
            if upload_file(conn, local, remote):
                print(f"✅ {local} загружен")
        
        # Собираем фронтенд
        print("\n🔨 Сборка фронтенда...")
        template_path = "/root/shannon/template"
        output, error, code = conn.execute(f"cd {template_path} && npm run build 2>&1")
        
        if code == 0:
            print("✅ Фронтенд собран успешно")
            if output:
                lines = output.split('\n')
                print("\n".join(lines[-10:]))
            
            # Перезагружаем Nginx
            print("\n🔄 Перезагрузка Nginx...")
            conn.execute("systemctl reload nginx")
            
            print("\n✅ Готово!")
        else:
            print(f"❌ Ошибка сборки:")
            if output:
                lines = output.split('\n')
                error_lines = [line for line in lines if 'error' in line.lower() or 'ERROR' in line]
                if error_lines:
                    print("\n".join(error_lines[:30]))
                else:
                    print(output[-500:])
        
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


