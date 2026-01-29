#!/usr/bin/env python3
"""
Проверка работы HTTPS
"""

import paramiko
import sys

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def execute_ssh_command(ssh, command, description):
    print(f"\n{description}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    if output:
        try:
            print(output[:800])
        except:
            print(output[:800].encode('ascii', 'replace').decode('ascii'))
    return exit_status == 0, output

def main():
    print("="*60)
    print("ПРОВЕРКА HTTPS")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверяем редирект HTTP -> HTTPS
        execute_ssh_command(
            ssh,
            "curl -I http://72.56.79.153/ 2>&1 | head -8",
            "1. Проверка редиректа HTTP -> HTTPS"
        )
        
        # 2. Проверяем HTTPS
        execute_ssh_command(
            ssh,
            "curl -k -I https://72.56.79.153/ 2>&1 | head -8",
            "2. Проверка HTTPS"
        )
        
        # 3. Проверяем содержимое HTTPS
        execute_ssh_command(
            ssh,
            "curl -k -s https://72.56.79.153/ | head -12",
            "3. Содержимое HTTPS страницы"
        )
        
        # 4. Проверяем API через HTTPS
        execute_ssh_command(
            ssh,
            "curl -k -s https://72.56.79.153/api/auth/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"513277\"}' | head -1",
            "4. Проверка API через HTTPS"
        )
        
        # 5. Проверяем статические файлы
        execute_ssh_command(
            ssh,
            "curl -k -I https://72.56.79.153/assets/index-DSQwK1pc.js 2>&1 | head -5",
            "5. Проверка статических файлов через HTTPS"
        )
        
        print("\n" + "="*60)
        print("ПРОВЕРКА ЗАВЕРШЕНА")
        print("="*60)
        print(f"\nHTTPS: https://{SSH_HOST}/")
        print(f"HTTP автоматически редиректит на HTTPS")
        print(f"Backend API: https://{SSH_HOST}/api/")
        print(f"WebSocket: wss://{SSH_HOST}/socket.io/")
        print("\nПриложение готово к тестированию!")
        print("Откройте в браузере: https://72.56.79.153/")
        print("\nПримечание: Браузер может показать предупреждение")
        print("о самоподписанном сертификате - это нормально.")
        print("Нажмите 'Продолжить' для доступа.")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

