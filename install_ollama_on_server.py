#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для установки Ollama на сервер и настройки модели для пентестинга
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_server_resources(conn):
    """Проверяет ресурсы сервера"""
    print("\n" + "="*60)
    print("🔍 Проверка ресурсов сервера...")
    print("="*60)
    
    # CPU информация
    print("\n📊 CPU:")
    output, error, code = conn.execute("lscpu | grep -E '^Model name|^CPU\\(s\\)|^Thread|^Core'")
    if output:
        print(output)
    
    # RAM информация
    print("\n💾 RAM:")
    output, error, code = conn.execute("free -h")
    if output:
        print(output)
        # Извлекаем общую RAM
        lines = output.split('\n')
        for line in lines:
            if 'Mem:' in line:
                parts = line.split()
                if len(parts) >= 2:
                    total_ram = parts[1]
                    print(f"   Общая RAM: {total_ram}")
    
    # Диск информация
    print("\n💿 Диск:")
    output, error, code = conn.execute("df -h /")
    if output:
        print(output)
    
    # Проверка GPU (если есть)
    print("\n🎮 GPU:")
    output, error, code = conn.execute("lspci | grep -i vga || lspci | grep -i nvidia || echo 'GPU не обнаружен'")
    if output:
        print(output.strip())
    
    return True

def check_ollama_installed(conn):
    """Проверяет, установлен ли Ollama"""
    print("\n" + "="*60)
    print("🔍 Проверка установки Ollama...")
    print("="*60)
    
    output, error, code = conn.execute("which ollama")
    if output and 'ollama' in output:
        print("✅ Ollama уже установлен")
        output, error, code = conn.execute("ollama --version")
        if output:
            print(f"   Версия: {output.strip()}")
        return True
    else:
        print("❌ Ollama не установлен")
        return False

def install_ollama(conn):
    """Устанавливает Ollama"""
    print("\n" + "="*60)
    print("📦 Установка Ollama...")
    print("="*60)
    
    # Проверяем, установлен ли curl
    output, error, code = conn.execute("which curl")
    if not output or 'curl' not in output:
        print("⚠️  curl не найден, устанавливаем...")
        conn.execute("apt-get update && apt-get install -y curl")
    
    # Устанавливаем Ollama через официальный скрипт
    print("\n📥 Скачивание и установка Ollama...")
    output, error, code = conn.execute("curl -fsSL https://ollama.com/install.sh | sh")
    
    if code == 0:
        print("✅ Ollama успешно установлен")
        # Проверяем версию
        output, error, code = conn.execute("ollama --version")
        if output:
            print(f"   Версия: {output.strip()}")
        return True
    else:
        print(f"❌ Ошибка установки Ollama")
        print(f"   Error: {error}")
        return False

def check_ollama_service(conn):
    """Проверяет статус Ollama service"""
    print("\n" + "="*60)
    print("🔍 Проверка Ollama service...")
    print("="*60)
    
    # Проверяем, запущен ли Ollama
    output, error, code = conn.execute("systemctl is-active ollama 2>/dev/null || echo 'not-found'")
    if output and 'active' in output:
        print("✅ Ollama service активен")
        return True
    else:
        print("⚠️  Ollama service не найден или не активен")
        # Пытаемся запустить Ollama вручную для проверки
        print("   Проверяем, работает ли Ollama...")
        output, error, code = conn.execute("curl -s http://localhost:11434/api/tags 2>&1 | head -5")
        if output and ('models' in output or '[]' in output):
            print("✅ Ollama работает на порту 11434")
            return True
        else:
            print("❌ Ollama не отвечает на порту 11434")
            return False

def recommend_model(conn):
    """Рекомендует модель на основе ресурсов сервера"""
    print("\n" + "="*60)
    print("🤖 Рекомендация модели...")
    print("="*60)
    
    # Получаем RAM в GB
    output, error, code = conn.execute("free -g | grep Mem | awk '{print $2}'")
    ram_gb = 0
    if output:
        try:
            ram_gb = int(output.strip())
        except:
            pass
    
    print(f"\n💾 Доступная RAM: {ram_gb} GB")
    
    # Рекомендации на основе RAM
    if ram_gb >= 16:
        recommended = "llama3.1:8b"  # 8B модель для мощных серверов
        alternatives = ["mistral", "neural-chat"]
        print(f"✅ Рекомендуется: {recommended} (8B параметров)")
        print(f"   Альтернативы: {', '.join(alternatives)}")
    elif ram_gb >= 8:
        recommended = "llama3.2:3b"  # 3B модель для средних серверов
        alternatives = ["mistral:7b", "neural-chat:7b"]
        print(f"✅ Рекомендуется: {recommended} (3B параметров)")
        print(f"   Альтернативы: {', '.join(alternatives)}")
    else:
        recommended = "llama3.2:1b"  # 1B модель для слабых серверов
        alternatives = ["tinyllama"]
        print(f"⚠️  Рекомендуется: {recommended} (1B параметров)")
        print(f"   Альтернативы: {', '.join(alternatives)}")
        print("   ⚠️  Внимание: Модель может быть медленной на этом сервере")
    
    return recommended

def setup_ollama_service(conn):
    """Настраивает systemd service для Ollama"""
    print("\n" + "="*60)
    print("⚙️  Настройка systemd service для Ollama...")
    print("="*60)
    
    service_content = """[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=root
Group=root
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0:11434"

[Install]
WantedBy=default.target
"""
    
    # Создаем service файл
    print("\n📝 Создание service файла...")
    conn.execute("cat > /etc/systemd/system/ollama.service << 'EOFSERVICE'\n" + service_content + "EOFSERVICE")
    
    # Перезагружаем systemd
    print("🔄 Перезагрузка systemd...")
    conn.execute("systemctl daemon-reload")
    
    # Включаем автозапуск
    print("✅ Включение автозапуска...")
    conn.execute("systemctl enable ollama")
    
    # Запускаем service
    print("🚀 Запуск Ollama service...")
    output, error, code = conn.execute("systemctl start ollama")
    
    if code == 0:
        # Ждем немного для запуска
        import time
        time.sleep(3)
        
        # Проверяем статус
        output, error, code = conn.execute("systemctl status ollama --no-pager | head -10")
        if output:
            print("\n📊 Статус service:")
            print(output)
        
        return True
    else:
        print(f"❌ Ошибка запуска service: {error}")
        return False

def pull_model(conn, model_name):
    """Загружает модель Ollama"""
    print("\n" + "="*60)
    print(f"📥 Загрузка модели {model_name}...")
    print("="*60)
    print("⏳ Это может занять несколько минут...")
    
    # Запускаем загрузку модели
    # Используем nohup чтобы процесс не прервался при разрыве соединения
    output, error, code = conn.execute(f"ollama pull {model_name}")
    
    if code == 0:
        print(f"✅ Модель {model_name} успешно загружена")
        
        # Проверяем список моделей
        output, error, code = conn.execute("ollama list")
        if output:
            print("\n📋 Установленные модели:")
            print(output)
        
        return True
    else:
        print(f"❌ Ошибка загрузки модели: {error}")
        return False

def test_ollama_api(conn):
    """Тестирует Ollama API"""
    print("\n" + "="*60)
    print("🧪 Тестирование Ollama API...")
    print("="*60)
    
    # Проверяем список моделей через API
    output, error, code = conn.execute("curl -s http://localhost:11434/api/tags")
    if output and 'models' in output:
        print("✅ API отвечает корректно")
        print(f"   Ответ: {output[:200]}...")
        return True
    else:
        print("❌ API не отвечает")
        print(f"   Output: {output}")
        print(f"   Error: {error}")
        return False

def main():
    """Главная функция"""
    print("="*60)
    print("🚀 Установка и настройка Ollama для пентестинга")
    print("="*60)
    
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        # 1. Проверка ресурсов
        check_server_resources(conn)
        
        # 2. Проверка установки Ollama
        ollama_installed = check_ollama_installed(conn)
        
        # 3. Установка Ollama (если не установлен)
        if not ollama_installed:
            if not install_ollama(conn):
                print("\n❌ Не удалось установить Ollama")
                return False
        
        # 4. Настройка systemd service
        if not check_ollama_service(conn):
            if not setup_ollama_service(conn):
                print("\n⚠️  Не удалось настроить service, но Ollama может работать")
        
        # 5. Рекомендация модели
        recommended_model = recommend_model(conn)
        
        # 6. Загрузка модели
        print(f"\n❓ Загрузить модель {recommended_model}? (y/n)")
        # Автоматически выбираем модель для пентестинга
        # Используем llama3.2:3b как оптимальный баланс для пентестинга
        model_to_use = "llama3.2:3b"  # Хороший баланс скорости и качества
        
        # Проверяем, загружена ли уже модель
        output, error, code = conn.execute("ollama list")
        if output and 'llama3.2' in output:
            print(f"✅ Модель llama3.2 уже загружена")
        else:
            if not pull_model(conn, model_to_use):
                print(f"\n⚠️  Не удалось загрузить модель {model_to_use}")
                print("   Вы можете загрузить её позже командой: ollama pull llama3.2:3b")
        
        # 7. Тестирование API
        if not test_ollama_api(conn):
            print("\n⚠️  API не отвечает, но это может быть временно")
        
        print("\n" + "="*60)
        print("✅ Установка завершена!")
        print("="*60)
        print(f"\n📝 Следующие шаги:")
        print(f"   1. Добавьте в .env Laravel:")
        print(f"      OLLAMA_API_URL=http://localhost:11434/api")
        print(f"      OLLAMA_MODEL=llama3.2:3b")
        print(f"   2. Проверьте работу: curl http://localhost:11434/api/tags")
        print(f"   3. Протестируйте модель: ollama run llama3.2:3b 'Hello'")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    main()

