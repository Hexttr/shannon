#!/usr/bin/env python3
"""
Удаление редиректа на HTTPS из конфигурации pentest
"""

import paramiko
import sys

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def execute_ssh_command(ssh, command, description):
    """Выполняет команду через SSH и выводит результат"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Выполняю: {command}")
    
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    
    output = stdout.read().decode('utf-8', errors='replace')
    errors = stderr.read().decode('utf-8', errors='replace')
    
    if output:
        try:
            print(output)
        except UnicodeEncodeError:
            print(output.encode('ascii', 'replace').decode('ascii'))
    if errors:
        try:
            print(f"Ошибки: {errors}", file=sys.stderr)
        except UnicodeEncodeError:
            print(f"Ошибки: {errors.encode('ascii', 'replace').decode('ascii')}", file=sys.stderr)
    
    return exit_status == 0, output

def main():
    print("="*60)
    print("УДАЛЕНИЕ РЕДИРЕКТА НА HTTPS")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        print("Подключение установлено!")
    except Exception as e:
        print(f"Ошибка подключения: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 1. Проверяем активные конфигурации
        print("\n1. Проверяю активные конфигурации...")
        execute_ssh_command(
            ssh,
            "ls -la /etc/nginx/sites-enabled/",
            "Активные конфигурации"
        )
        
        # 2. Отключаем конфигурацию pentest если она активна
        print("\n2. Отключаю конфигурацию pentest...")
        execute_ssh_command(
            ssh,
            "rm -f /etc/nginx/sites-enabled/pentest",
            "Отключение pentest конфигурации"
        )
        
        # 3. Проверяем конфигурацию pentest и убираем редирект
        print("\n3. Убираю редирект из конфигурации pentest...")
        execute_ssh_command(
            ssh,
            "cat /etc/nginx/sites-available/pentest",
            "Текущая конфигурация pentest"
        )
        
        # Читаем конфигурацию и убираем редирект
        stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-available/pentest 2>/dev/null || echo ''")
        pentest_config = stdout.read().decode('utf-8', errors='replace')
        
        if pentest_config:
            # Убираем строки с редиректом на HTTPS
            lines = pentest_config.split('\n')
            updated_lines = []
            for line in lines:
                if 'return 301 https://' in line or 'return 302 https://' in line:
                    print(f"Удаляю строку: {line.strip()}")
                    continue
                updated_lines.append(line)
            
            updated_config = '\n'.join(updated_lines)
            
            stdin, stdout, stderr = ssh.exec_command(f"cat > /etc/nginx/sites-available/pentest << 'PENTEST_EOF'\n{updated_config}\nPENTEST_EOF\n")
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status == 0:
                print("Конфигурация pentest обновлена!")
        
        # 4. Убеждаемся что только shannon активна
        print("\n4. Проверяю активные конфигурации...")
        execute_ssh_command(
            ssh,
            "ls -la /etc/nginx/sites-enabled/",
            "Активные конфигурации после отключения"
        )
        
        # 5. Проверяем приоритет конфигураций
        print("\n5. Проверяю приоритет конфигураций...")
        execute_ssh_command(
            ssh,
            "nginx -T 2>/dev/null | grep -A 20 'server_name.*72.56.79.153' | head -40",
            "Все server блоки для 72.56.79.153"
        )
        
        # 6. Проверяем и перезапускаем nginx
        print("\n6. Проверяю и перезапускаю nginx...")
        execute_ssh_command(ssh, "nginx -t", "Проверка конфигурации")
        execute_ssh_command(ssh, "systemctl reload nginx", "Перезагрузка nginx")
        
        # 7. Тестируем редиректы
        print("\n7. Тестирую редиректы...")
        execute_ssh_command(
            ssh,
            "curl -I http://72.56.79.153/ 2>&1",
            "Проверка HTTP заголовков"
        )
        
        execute_ssh_command(
            ssh,
            "curl -L http://72.56.79.153/ 2>&1 | head -20",
            "Проверка содержимого после редиректов"
        )
        
        # 8. Финальная проверка
        print("\n8. Финальная проверка...")
        execute_ssh_command(
            ssh,
            "curl -v http://72.56.79.153/ 2>&1 | grep -E 'HTTP|Location|location' | head -10",
            "Проверка редиректов в деталях"
        )
        
        print("\n" + "="*60)
        print("ИСПРАВЛЕНИЕ ЗАВЕРШЕНО")
        print("="*60)
        print(f"\nHTTP: http://{SSH_HOST}/")
        print(f"Backend API: http://{SSH_HOST}/api/")
        print("\nРедиректы на HTTPS удалены.")
        print("Проверьте работу в браузере: http://72.56.79.153/")
        
    except Exception as e:
        print(f"\nКритическая ошибка: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        ssh.close()
        print("\nСоединение закрыто.")

if __name__ == "__main__":
    main()

