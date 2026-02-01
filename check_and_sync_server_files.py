#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка и синхронизация файлов на сервере
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_git_status(conn):
    """Проверяет статус git на сервере"""
    print("\n" + "="*60)
    print("🔍 Проверка статуса Git на сервере...")
    print("="*60)
    
    # Переходим в директорию проекта
    conn.execute("cd /root/shannon && pwd")
    
    # Проверяем текущую ветку
    output, error, code = conn.execute("cd /root/shannon && git branch --show-current")
    if output:
        current_branch = output.strip()
        print(f"\n📌 Текущая ветка: {current_branch}")
    
    # Проверяем статус
    output, error, code = conn.execute("cd /root/shannon && git status --short")
    if output:
        print("\n📝 Изменения в рабочей директории:")
        print(output)
    else:
        print("\n✅ Рабочая директория чистая")
    
    # Проверяем, есть ли новые коммиты в удаленном репозитории
    output, error, code = conn.execute("cd /root/shannon && git fetch origin ollama 2>&1")
    
    output, error, code = conn.execute("cd /root/shannon && git log HEAD..origin/ollama --oneline")
    if output:
        print("\n⬇️  Новые коммиты для загрузки:")
        print(output)
        return True
    else:
        print("\n✅ Локальная ветка синхронизирована с удаленной")
        return False

def sync_files(conn):
    """Синхронизирует файлы с удаленного репозитория"""
    print("\n" + "="*60)
    print("🔄 Синхронизация файлов...")
    print("="*60)
    
    # Переключаемся на ветку ollama если нужно
    output, error, code = conn.execute("cd /root/shannon && git checkout ollama 2>&1")
    if output:
        print(f"   {output.strip()}")
    
    # Выполняем pull
    print("\n📥 Загрузка изменений из Git...")
    output, error, code = conn.execute("cd /root/shannon && git pull origin ollama")
    
    if code == 0:
        print("✅ Файлы успешно синхронизированы")
        if output:
            print(f"\n   {output}")
        return True
    else:
        print(f"❌ Ошибка синхронизации: {error}")
        return False

def check_new_files(conn):
    """Проверяет наличие новых файлов на сервере"""
    print("\n" + "="*60)
    print("🔍 Проверка новых файлов...")
    print("="*60)
    
    files_to_check = [
        "backend-laravel/app/Services/Contracts/AiAnalysisServiceInterface.php",
        "backend-laravel/app/Services/OllamaApiService.php",
        "backend-laravel/app/Services/AiServiceFactory.php",
    ]
    
    all_exist = True
    for file_path in files_to_check:
        full_path = f"/root/shannon/{file_path}"
        output, error, code = conn.execute(f"test -f {full_path} && echo 'exists' || echo 'not-found'")
        if 'exists' in output:
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - НЕ НАЙДЕН")
            all_exist = False
    
    return all_exist

def check_modified_files(conn):
    """Проверяет измененные файлы"""
    print("\n" + "="*60)
    print("🔍 Проверка измененных файлов...")
    print("="*60)
    
    files_to_check = [
        "backend-laravel/app/Services/ClaudeApiService.php",
        "backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php",
        "backend-laravel/app/Data/Pentests/PentestConfigData.php",
        "backend-laravel/app/Http/Requests/CreatePentestRequest.php",
        "backend-laravel/config/services.php",
    ]
    
    for file_path in files_to_check:
        full_path = f"/root/shannon/{file_path}"
        output, error, code = conn.execute(f"test -f {full_path} && echo 'exists' || echo 'not-found'")
        if 'exists' in output:
            # Проверяем содержимое на наличие ключевых изменений
            if 'OllamaApiService' in file_path or 'AiServiceFactory' in file_path:
                print(f"✅ {file_path}")
            elif 'ClaudeApiService' in file_path:
                output2, _, _ = conn.execute(f"grep -q 'AiAnalysisServiceInterface' {full_path} && echo 'updated' || echo 'old'")
                if 'updated' in output2:
                    print(f"✅ {file_path} - обновлен")
                else:
                    print(f"⚠️  {file_path} - возможно старая версия")
            elif 'PentestEngine' in file_path:
                output2, _, _ = conn.execute(f"grep -q 'AiServiceFactory' {full_path} && echo 'updated' || echo 'old'")
                if 'updated' in output2:
                    print(f"✅ {file_path} - обновлен")
                else:
                    print(f"⚠️  {file_path} - возможно старая версия")
            elif 'PentestConfigData' in file_path:
                output2, _, _ = conn.execute(f"grep -q 'aiProvider' {full_path} && echo 'updated' || echo 'old'")
                if 'updated' in output2:
                    print(f"✅ {file_path} - обновлен")
                else:
                    print(f"⚠️  {file_path} - возможно старая версия")
            elif 'CreatePentestRequest' in file_path:
                output2, _, _ = conn.execute(f"grep -q 'aiProvider' {full_path} && echo 'updated' || echo 'old'")
                if 'updated' in output2:
                    print(f"✅ {file_path} - обновлен")
                else:
                    print(f"⚠️  {file_path} - возможно старая версия")
            elif 'services.php' in file_path:
                output2, _, _ = conn.execute(f"grep -q 'ollama' {full_path} && echo 'updated' || echo 'old'")
                if 'updated' in output2:
                    print(f"✅ {file_path} - обновлен")
                else:
                    print(f"⚠️  {file_path} - возможно старая версия")
        else:
            print(f"❌ {file_path} - НЕ НАЙДЕН")

def main():
    """Главная функция"""
    print("="*60)
    print("🔍 Проверка и синхронизация файлов на сервере")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        # 1. Проверка статуса git
        has_updates = check_git_status(conn)
        
        # 2. Синхронизация если есть обновления
        if has_updates:
            if not sync_files(conn):
                print("\n⚠️  Не удалось синхронизировать файлы")
                return False
        
        # 3. Проверка новых файлов
        if not check_new_files(conn):
            print("\n⚠️  Некоторые новые файлы отсутствуют")
            if has_updates:
                print("   Попробуйте выполнить git pull вручную")
        
        # 4. Проверка измененных файлов
        check_modified_files(conn)
        
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


