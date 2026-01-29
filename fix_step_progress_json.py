#!/usr/bin/env python3
"""
Исправление формата step_progress в БД
"""

import paramiko
import json
import re

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def fix_json_string(s):
    """Преобразует неправильный JSON в правильный"""
    if not s or s == 'None':
        return None
    
    # Заменяем одинарные кавычки на двойные
    s = s.replace("'", '"')
    
    # Если ключи без кавычек, добавляем кавычки
    # Паттерн: {key: value} -> {"key": "value"}
    def add_quotes_to_keys(match):
        content = match.group(1)
        # Заменяем ключи без кавычек
        content = re.sub(r'(\w+):', r'"\1":', content)
        # Заменяем значения без кавычек (если это строки)
        content = re.sub(r':\s*(\w+)(?=[,}])', r': "\1"', content)
        return '{' + content + '}'
    
    # Обрабатываем объекты без кавычек
    s = re.sub(r'\{([^}]+)\}', add_quotes_to_keys, s)
    
    return s

def main():
    print("="*60)
    print("ИСПРАВЛЕНИЕ ФОРМАТА step_progress")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверяем текущие данные
        print("\n1. ТЕКУЩИЕ ДАННЫЕ:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, step_progress FROM pentests;'")
        current_data = stdout.read().decode('utf-8', errors='replace')
        if current_data:
            print("  Текущие данные:")
            for line in current_data.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        pid, progress = parts[0], parts[1]
                        print(f"    ID: {pid}, step_progress: {progress}")
        
        # 2. Исправляем данные
        print("\n2. ИСПРАВЛЕНИЕ ДАННЫХ:")
        
        # Для каждого пентеста
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, step_progress FROM pentests WHERE step_progress IS NOT NULL AND step_progress != \"\";'")
        pentests_to_fix = stdout.read().decode('utf-8', errors='replace')
        
        if pentests_to_fix:
            for line in pentests_to_fix.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        pid, progress = parts[0], parts[1]
                        
                        if progress and progress != 'None':
                            # Преобразуем в правильный JSON
                            # Заменяем одинарные кавычки и добавляем кавычки к ключам
                            fixed = progress.replace("'", '"')
                            # Если ключи без кавычек: {key: value} -> {"key": "value"}
                            fixed = re.sub(r'(\w+):', r'"\1":', fixed)
                            # Если значения без кавычек (строки): : value -> : "value"
                            fixed = re.sub(r':\s*(\w+)(?=[,}])', r': "\1"', fixed)
                            
                            # Проверяем что это валидный JSON
                            try:
                                json.loads(fixed)
                                print(f"  [OK] Пентест {pid}: исправлен")
                                print(f"    Было: {progress[:80]}")
                                print(f"    Стало: {fixed[:80]}")
                                
                                # Обновляем в БД
                                # Экранируем кавычки для SQL
                                fixed_sql = fixed.replace('"', '\\"')
                                stdin, stdout, stderr = ssh.exec_command(f"sqlite3 /root/shannon/backend/shannon.db \"UPDATE pentests SET step_progress = '{fixed_sql}' WHERE id = {pid};\"")
                                stdout.channel.recv_exit_status()
                            except json.JSONDecodeError as e:
                                print(f"  [ERROR] Пентест {pid}: не удалось исправить - {e}")
                                # Если не получается исправить, устанавливаем NULL
                                stdin, stdout, stderr = ssh.exec_command(f"sqlite3 /root/shannon/backend/shannon.db \"UPDATE pentests SET step_progress = NULL WHERE id = {pid};\"")
                                stdout.channel.recv_exit_status()
                                print(f"    Установлено NULL")
        
        # 3. Проверяем результат
        print("\n3. ПРОВЕРКА РЕЗУЛЬТАТА:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 /root/shannon/backend/shannon.db 'SELECT id, step_progress FROM pentests;'")
        fixed_data = stdout.read().decode('utf-8', errors='replace')
        if fixed_data:
            print("  Исправленные данные:")
            for line in fixed_data.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        pid, progress = parts[0], parts[1]
                        if progress and progress != 'None':
                            try:
                                json.loads(progress)
                                print(f"    ID: {pid}: [OK] Валидный JSON")
                            except:
                                print(f"    ID: {pid}: [ERROR] Невалидный JSON: {progress[:80]}")
        
        # 4. Перезапускаем backend
        print("\n4. ПЕРЕЗАПУСК BACKEND:")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart shannon-backend.service")
        stdout.channel.recv_exit_status()
        print("  [OK] Backend перезапущен")
        
        # 5. Тестируем API
        print("\n5. ТЕСТИРОВАНИЕ API:")
        import time
        time.sleep(3)
        
        # Получаем токен
        stdin, stdout, stderr = ssh.exec_command("curl -s -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"513277\"}' 2>&1")
        login_response = stdout.read().decode('utf-8', errors='replace')
        
        if 'access_token' in login_response:
            import json as json_lib
            login_data = json_lib.loads(login_response)
            token = login_data.get('access_token')
            
            # Тестируем API
            stdin, stdout, stderr = ssh.exec_command(f"curl -s -H 'Authorization: Bearer {token}' http://localhost:8000/api/pentests 2>&1")
            api_response = stdout.read().decode('utf-8', errors='replace')
            
            try:
                pentests = json_lib.loads(api_response)
                if isinstance(pentests, list):
                    print(f"  [OK] API возвращает {len(pentests)} пентестов")
                    for p in pentests[:3]:
                        if isinstance(p, dict):
                            print(f"    ID: {p.get('id')}, Имя: {p.get('name', '')[:30]}, Статус: {p.get('status')}")
                else:
                    print(f"  [WARNING] Неожиданный формат ответа: {type(pentests)}")
            except json_lib.JSONDecodeError:
                print(f"  [ERROR] Не удалось распарсить ответ: {api_response[:200]}")
        
        print("\n" + "="*60)
        print("ГОТОВО")
        print("="*60)
        print("\n[SUCCESS] Данные исправлены, API должно работать")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

