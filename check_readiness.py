#!/usr/bin/env python3
"""
Проверка готовности системы к пентесту
"""

import paramiko

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def check_tool(ssh, tool_name):
    """Проверяет установлен ли инструмент"""
    stdin, stdout, stderr = ssh.exec_command(f"which {tool_name}")
    return stdout.channel.recv_exit_status() == 0

def main():
    print("="*60)
    print("ПРОВЕРКА ГОТОВНОСТИ К ПЕНТЕСТУ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Проверка инструментов
        print("\n1. ИНСТРУМЕНТЫ ПЕНТЕСТИНГА:")
        tools = ["nmap", "nikto", "sqlmap", "nuclei", "dirb", "gobuster", "wpscan", "whatweb", "subfinder", "httpx"]
        installed = []
        missing = []
        
        for tool in tools:
            if check_tool(ssh, tool):
                installed.append(tool)
                print(f"  [OK] {tool}")
            else:
                missing.append(tool)
                print(f"  [ERROR] {tool}")
        
        print(f"\n  Итого: {len(installed)}/{len(tools)} установлено")
        
        # Проверка backend
        print("\n2. BACKEND:")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'uvicorn|python.*app.main' | grep -v grep")
        backend_running = stdout.read().decode('utf-8', errors='replace').strip()
        if backend_running:
            print("  [OK] Backend работает")
        else:
            print("  [ERROR] Backend не запущен")
        
        # Проверка frontend
        print("\n3. FRONTEND:")
        stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/shannon/index.html")
        if stdout.channel.recv_exit_status() == 0:
            print("  [OK] Frontend развернут")
        else:
            print("  [ERROR] Frontend не найден")
        
        # Проверка nginx
        print("\n4. NGINX:")
        stdin, stdout, stderr = ssh.exec_command("systemctl is-active nginx")
        nginx_status = stdout.read().decode('utf-8', errors='replace').strip()
        if nginx_status == "active":
            print("  [OK] Nginx работает")
        else:
            print(f"  [ERROR] Nginx статус: {nginx_status}")
        
        # Итоговый статус
        print("\n" + "="*60)
        print("ИТОГОВЫЙ СТАТУС")
        print("="*60)
        
        all_ready = len(installed) == len(tools) and backend_running and nginx_status == "active"
        
        if all_ready:
            print("\n[SUCCESS] Система готова к пентесту!")
            print("\nСледующие шаги:")
            print("1. Откройте https://72.56.79.153/")
            print("2. Войдите (admin/513277)")
            print("3. Перейдите в раздел 'Сервисы' и создайте сервис")
            print("4. Перейдите в раздел 'Пентесты' и создайте новый пентест")
            print("5. Запустите пентест")
        else:
            print("\n[WARN] Система не полностью готова")
            if missing:
                print(f"  Не установлены инструменты: {', '.join(missing)}")
            if not backend_running:
                print("  Backend не запущен")
            if nginx_status != "active":
                print("  Nginx не работает")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

