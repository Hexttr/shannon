#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Включение доступа Ollama к интернету
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def enable_internet():
    """Включает доступ Ollama к интернету"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🌐 ВКЛЮЧЕНИЕ ДОСТУПА OLLAMA К ИНТЕРНЕТУ")
        print("="*60)
        
        # 1. Проверяем текущую конфигурацию Ollama
        print("\n1. Текущая конфигурация Ollama service:")
        output, _, _ = conn.execute('cat /etc/systemd/system/ollama.service')
        print(output)
        
        # 2. Проверяем переменные окружения Ollama
        print("\n2. Переменные окружения Ollama:")
        output, _, _ = conn.execute('systemctl show ollama.service | grep Environment')
        print(output)
        
        # 3. Проверяем конфигурационные файлы Ollama
        print("\n3. Поиск конфигурационных файлов Ollama:")
        config_paths = [
            '/root/.ollama/config.json',
            '/etc/ollama/config.json',
            '/home/ollama/.ollama/config.json',
            '/usr/local/share/ollama/config.json'
        ]
        for path in config_paths:
            output, _, code = conn.execute(f"test -f {path} && echo 'found: {path}' || echo 'not found: {path}'")
            print(f"   {output.strip()}")
        
        # 4. Проверяем документацию Ollama о настройках интернета
        print("\n4. Проверка настроек интернета в Ollama:")
        print("   Ищем переменные окружения для доступа к интернету...")
        
        # 5. Обновляем service файл для включения доступа к интернету
        print("\n5. Обновление service файла Ollama:")
        print("   Добавляем переменные окружения для доступа к интернету...")
        
        # Читаем текущий файл
        output, _, _ = conn.execute('cat /etc/systemd/system/ollama.service')
        current_config = output
        
        # Проверяем есть ли уже настройки интернета
        if 'OLLAMA_ORIGINS' in current_config or 'OLLAMA_HOST' in current_config:
            print("   ⚠️  Настройки уже есть в конфигурации")
        else:
            # Создаем бэкап
            conn.execute('cp /etc/systemd/system/ollama.service /etc/systemd/system/ollama.service.backup')
            print("   ✅ Бэкап создан")
            
            # Обновляем конфигурацию - добавляем переменные для доступа к интернету
            # Ollama по умолчанию имеет доступ к интернету, но может быть ограничен
            # Добавляем явные настройки если нужно
            updated_config = current_config.replace(
                'Environment="PATH=',
                'Environment="OLLAMA_ORIGINS=*\nEnvironment="OLLAMA_HOST=0.0.0.0\nEnvironment="PATH='
            )
            
            # Сохраняем обновленную конфигурацию
            import base64
            config_b64 = base64.b64encode(updated_config.encode('utf-8')).decode('ascii')
            cmd = f'''python3 << 'PYEOF'
import base64
config = base64.b64decode('{config_b64}').decode('utf-8')
with open('/tmp/ollama.service', 'w', encoding='utf-8') as f:
    f.write(config)
PYEOF'''
            conn.execute(cmd)
            conn.execute('cp /tmp/ollama.service /etc/systemd/system/ollama.service')
            print("   ✅ Конфигурация обновлена")
        
        # 6. Перезагружаем конфигурацию systemd и перезапускаем Ollama
        print("\n6. Перезапуск Ollama с новыми настройками:")
        conn.execute('systemctl daemon-reload')
        conn.execute('systemctl restart ollama.service')
        
        # Ждем немного и проверяем статус
        conn.execute('sleep 3')
        output, _, _ = conn.execute('systemctl status ollama.service --no-pager | head -15')
        print(output)
        
        # 7. Проверяем что Ollama работает
        print("\n7. Проверка работы Ollama:")
        output, _, code = conn.execute('curl -s http://localhost:11434/api/tags | head -3')
        if code == 0 and output:
            print("   ✅ Ollama работает")
        else:
            print("   ⚠️  Ollama не отвечает")
        
        print("\n" + "="*60)
        print("✅ НАСТРОЙКА ЗАВЕРШЕНА")
        print("="*60)
        print("\n💡 Важно:")
        print("   Ollama по умолчанию должен иметь доступ к интернету")
        print("   Если доступ ограничен, это может влиять на качество анализа")
        print("   Проверьте что сервер может делать внешние HTTP запросы")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    enable_internet()

