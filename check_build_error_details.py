#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка деталей ошибки сборки
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_build_error(conn):
    """Проверяет детали ошибки сборки"""
    print("\n" + "="*60)
    print("🔍 Проверка деталей ошибки сборки...")
    print("="*60)
    
    template_path = "/root/shannon/template"
    
    # Пробуем собрать с более подробным выводом
    print("\n🔨 Попытка сборки с подробным выводом...")
    output, error, code = conn.execute(f"cd {template_path} && npm run build 2>&1 | tail -n 50")
    
    if output:
        print("Вывод сборки:")
        print(output)
    
    # Проверяем версию Node.js
    print("\n🔍 Проверка версии Node.js...")
    output2, error2, code2 = conn.execute("node --version")
    if output2:
        print(f"Node.js версия: {output2.strip()}")
    
    # Проверяем архитектуру
    print("\n🔍 Проверка архитектуры...")
    output3, error3, code3 = conn.execute("uname -m")
    if output3:
        print(f"Архитектура: {output3.strip()}")
    
    # Проверяем, может быть dist уже существует где-то
    print("\n🔍 Поиск существующего dist...")
    output4, error4, code4 = conn.execute("find /root/shannon -name 'dist' -type d 2>&1")
    if output4:
        print("Найденные директории dist:")
        print(output4)

def try_alternative_build(conn):
    """Пробует альтернативный способ сборки"""
    print("\n" + "="*60)
    print("🔧 Альтернативный способ сборки...")
    print("="*60)
    
    template_path = "/root/shannon/template"
    
    # Пробуем собрать через vite напрямую с флагом --force
    print("\n🔨 Сборка через vite с --force...")
    output, error, code = conn.execute(f"cd {template_path} && npx vite build --force 2>&1")
    
    if code == 0:
        print("✅ Сборка успешна!")
        if output:
            lines = output.split('\n')
            print("\n".join(lines[-10:]))
        return True
    else:
        print(f"❌ Ошибка:")
        if output:
            print(output[-300:])
        return False

def main():
    """Главная функция"""
    print("="*60)
    print("🔍 Проверка деталей ошибки сборки")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        check_build_error(conn)
        try_alternative_build(conn)
        
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


