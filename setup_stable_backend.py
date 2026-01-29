#!/usr/bin/env python3
"""
Настройка стабильного backend через systemd
"""

import paramiko
import time

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def main():
    print("="*60)
    print("НАСТРОЙКА СТАБИЛЬНОГО BACKEND")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Останавливаем все процессы
        print("\n1. ОСТАНОВКА СТАРЫХ ПРОЦЕССОВ:")
        ssh.exec_command("pkill -f 'uvicorn'")
        ssh.exec_command("pkill -f 'python.*app.main'")
        time.sleep(2)
        print("  [OK] Остановлено")
        
        # 2. Устанавливаем зависимости системно
        print("\n2. УСТАНОВКА ЗАВИСИМОСТЕЙ (СИСТЕМНО):")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && python3 -m pip install --user -q -r requirements.txt 2>&1 | tail -5")
        install_output = stdout.read().decode('utf-8', errors='replace')
        if install_output:
            print(f"  {install_output}")
        
        # Проверяем установку
        stdin, stdout, stderr = ssh.exec_command("python3 -c 'import uvicorn; import fastapi; import socketio; print(\"OK\")' 2>&1")
        check = stdout.read().decode('utf-8', errors='replace')
        check_err = stderr.read().decode('utf-8', errors='replace')
        if check_err:
            print(f"  [WARNING] {check_err[:200]}")
            # Пробуем установить через apt если нужно
            print("  Пробую установить через apt...")
            ssh.exec_command("apt-get update -qq && apt-get install -y python3-pip python3-venv > /dev/null 2>&1")
            stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend && pip3 install -q -r requirements.txt 2>&1 | tail -5")
        else:
            print(f"  [OK] Зависимости установлены: {check}")
        
        # 3. Создаем systemd service
        print("\n3. СОЗДАНИЕ SYSTEMD SERVICE:")
        service_content = """[Unit]
Description=Shannon Pentest Platform Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/shannon/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=append:/var/log/shannon-backend.log
StandardError=append:/var/log/shannon-backend-error.log

[Install]
WantedBy=multi-user.target
"""
        
        stdin, stdout, stderr = ssh.exec_command("cat > /etc/systemd/system/shannon-backend.service << 'EOFSERVICE'\n" + service_content + "\nEOFSERVICE")
        stdout.channel.recv_exit_status()
        print("  [OK] Service файл создан")
        
        # 4. Перезагружаем systemd и запускаем сервис
        print("\n4. ЗАПУСК СЕРВИСА:")
        stdin, stdout, stderr = ssh.exec_command("systemctl daemon-reload")
        stdout.channel.recv_exit_status()
        print("  [OK] Systemd перезагружен")
        
        stdin, stdout, stderr = ssh.exec_command("systemctl enable shannon-backend.service")
        stdout.channel.recv_exit_status()
        print("  [OK] Сервис включен в автозагрузку")
        
        stdin, stdout, stderr = ssh.exec_command("systemctl start shannon-backend.service")
        stdout.channel.recv_exit_status()
        time.sleep(5)
        print("  [OK] Сервис запущен")
        
        # 5. Проверяем статус
        print("\n5. ПРОВЕРКА СТАТУСА:")
        stdin, stdout, stderr = ssh.exec_command("systemctl status shannon-backend.service --no-pager | head -15")
        status = stdout.read().decode('utf-8', errors='replace')
        if status:
            print("  Статус сервиса:")
            for line in status.strip().split('\n')[:15]:
                if line:
                    safe_line = line.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_line}")
        
        # 6. Проверяем процесс и порт
        print("\n6. ПРОВЕРКА ПРОЦЕССА И ПОРТА:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'python.*uvicorn.*socketio_app' | grep -v grep")
        proc = stdout.read().decode('utf-8', errors='replace')
        if proc:
            print(f"  [OK] Процесс запущен:")
            print(f"    {proc[:150]}")
        else:
            print("  [ERROR] Процесс не найден")
        
        stdin, stdout, stderr = ssh.exec_command("netstat -tlnp 2>/dev/null | grep ':8000' || ss -tlnp 2>/dev/null | grep ':8000'")
        port = stdout.read().decode('utf-8', errors='replace')
        if port:
            print(f"  [OK] Порт 8000 слушается")
        else:
            print("  [ERROR] Порт не слушается")
        
        # 7. Тестируем API
        print("\n7. ТЕСТИРОВАНИЕ API:")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/health 2>&1")
        health = stdout.read().decode('utf-8', errors='replace')
        if health:
            print(f"  /health: {health}")
        
        stdin, stdout, stderr = ssh.exec_command("curl -s -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"513277\"}' 2>&1")
        login = stdout.read().decode('utf-8', errors='replace')
        if login:
            if 'access_token' in login:
                print("  /api/auth/login: [OK] Работает!")
            else:
                print(f"  /api/auth/login: {login[:200]}")
        
        # 8. Проверяем логи
        print("\n8. ПРОВЕРКА ЛОГОВ:")
        stdin, stdout, stderr = ssh.exec_command("tail -10 /var/log/shannon-backend.log 2>/dev/null")
        logs = stdout.read().decode('utf-8', errors='replace')
        if logs:
            print("  Последние логи:")
            for line in logs.strip().split('\n')[-5:]:
                if line:
                    safe_line = line.encode('ascii', 'replace').decode('ascii')
                    print(f"    {safe_line[:150]}")
        
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТ")
        print("="*60)
        
        if proc and port:
            print("\n[SUCCESS] Backend настроен и запущен!")
            print("\nОсобенности:")
            print("  - Запускается автоматически при загрузке системы")
            print("  - Автоматически перезапускается при падении")
            print("  - Логи в /var/log/shannon-backend.log")
            print("  - Ошибки в /var/log/shannon-backend-error.log")
            print("\nУправление:")
            print("  systemctl status shannon-backend.service  # статус")
            print("  systemctl restart shannon-backend.service  # перезапуск")
            print("  systemctl stop shannon-backend.service    # остановка")
            print("\nДоступен: https://72.56.79.153/api")
            print("Логин: admin")
            print("Пароль: 513277")
        else:
            print("\n[ERROR] Backend не запустился")
            print("Проверьте логи:")
            print("  tail -f /var/log/shannon-backend-error.log")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

