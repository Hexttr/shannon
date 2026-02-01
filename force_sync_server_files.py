#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Принудительная синхронизация файлов на сервере
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def force_sync(conn):
    """Принудительно синхронизирует файлы"""
    print("\n" + "="*60)
    print("🔄 Принудительная синхронизация файлов...")
    print("="*60)
    
    # Сохраняем локальные изменения в stash
    print("\n💾 Сохранение локальных изменений в stash...")
    output, error, code = conn.execute("cd /root/shannon && git stash push -m 'Local changes before sync'")
    if code == 0:
        print("✅ Локальные изменения сохранены")
    
    # Переключаемся на ветку ollama
    print("\n🔄 Переключение на ветку ollama...")
    output, error, code = conn.execute("cd /root/shannon && git checkout ollama 2>&1")
    if output:
        print(f"   {output.strip()}")
    
    # Выполняем pull
    print("\n📥 Загрузка изменений из Git...")
    output, error, code = conn.execute("cd /root/shannon && git pull origin ollama")
    
    if code == 0:
        print("✅ Файлы успешно синхронизированы")
        if output:
            print(f"\n   {output[:500]}")
        return True
    else:
        print(f"❌ Ошибка синхронизации: {error}")
        return False

def check_new_files(conn):
    """Проверяет наличие новых файлов"""
    print("\n" + "="*60)
    print("🔍 Проверка новых файлов...")
    print("="*60)
    
    files_to_check = [
        ("backend-laravel/app/Services/Contracts/AiAnalysisServiceInterface.php", "Интерфейс AI сервиса"),
        ("backend-laravel/app/Services/OllamaApiService.php", "Ollama API сервис"),
        ("backend-laravel/app/Services/AiServiceFactory.php", "Фабрика AI провайдеров"),
    ]
    
    all_exist = True
    for file_path, description in files_to_check:
        full_path = f"/root/shannon/{file_path}"
        output, error, code = conn.execute(f"test -f {full_path} && echo 'exists' || echo 'not-found'")
        if 'exists' in output:
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ {description}: {file_path} - НЕ НАЙДЕН")
            all_exist = False
    
    # Проверяем ключевые изменения в существующих файлах
    print("\n🔍 Проверка изменений в существующих файлах...")
    
    checks = [
        ("backend-laravel/app/Services/ClaudeApiService.php", "AiAnalysisServiceInterface", "ClaudeApiService реализует интерфейс"),
        ("backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php", "AiServiceFactory", "PentestEngine использует фабрику"),
        ("backend-laravel/app/Data/Pentests/PentestConfigData.php", "aiProvider", "PentestConfigData содержит aiProvider"),
        ("backend-laravel/app/Http/Requests/CreatePentestRequest.php", "aiProvider", "CreatePentestRequest валидирует aiProvider"),
        ("backend-laravel/config/services.php", "ollama", "Конфигурация Ollama добавлена"),
    ]
    
    for file_path, search_term, description in checks:
        full_path = f"/root/shannon/{file_path}"
        output, error, code = conn.execute(f"grep -q '{search_term}' {full_path} 2>&1 && echo 'found' || echo 'not-found'")
        if 'found' in output:
            print(f"✅ {description}")
        else:
            print(f"⚠️  {description} - не найдено")
    
    return all_exist

def main():
    """Главная функция"""
    print("="*60)
    print("🔄 Принудительная синхронизация файлов на сервере")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        # Синхронизация
        if force_sync(conn):
            # Проверка файлов
            if check_new_files(conn):
                print("\n" + "="*60)
                print("✅ Все файлы успешно синхронизированы и проверены")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("⚠️  Некоторые файлы отсутствуют, но синхронизация выполнена")
                print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()


