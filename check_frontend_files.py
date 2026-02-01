#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка фронтенд файлов на сервере
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_frontend_files(conn):
    """Проверяет фронтенд файлы"""
    print("\n" + "="*60)
    print("🔍 Проверка фронтенд файлов...")
    print("="*60)
    
    # Проверяем типы
    print("\n📝 Проверка типов...")
    file_path = "/root/shannon/template/src/types/index.ts"
    output, error, code = conn.execute(f"grep -q 'aiProvider' {file_path} 2>&1 && echo 'found' || echo 'not-found'")
    if 'found' in output:
        print("✅ types/index.ts содержит aiProvider")
    else:
        print("❌ types/index.ts не содержит aiProvider")
    
    # Проверяем форму создания пентеста
    print("\n📝 Проверка формы создания пентеста...")
    file_path = "/root/shannon/template/src/pages/Pentests.tsx"
    
    checks = [
        ("selectedAiProvider", "Состояние для выбора AI провайдера"),
        ("setSelectedAiProvider", "Функция установки AI провайдера"),
        ("aiProvider", "Поле aiProvider в config"),
        ("AI Модель", "Выбор модели в форме"),
    ]
    
    for search_term, description in checks:
        output, error, code = conn.execute(f"grep -q '{search_term}' {file_path} 2>&1 && echo 'found' || echo 'not-found'")
        if 'found' in output:
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - не найдено")
    
    return True

def main():
    """Главная функция"""
    print("="*60)
    print("🔍 Проверка фронтенд файлов на сервере")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        check_frontend_files(conn)
        
        print("\n" + "="*60)
        print("✅ Проверка завершена")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


