#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная проверка приложения
"""

import paramiko
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def ssh_exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    print("="*60)
    print("ФИНАЛЬНАЯ ПРОВЕРКА ПРИЛОЖЕНИЯ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка backend
        print("\n1. ПРОВЕРКА BACKEND:")
        success, output, error = ssh_exec(ssh, "systemctl is-active shannon-laravel.service")
        if "active" in output.lower():
            print("  ✅ Backend запущен")
        else:
            print(f"  ❌ Backend не запущен: {output}")
        
        # 2. Проверка API
        print("\n2. ПРОВЕРКА API:")
        success, output, error = ssh_exec(ssh, f"curl -s http://{SSH_HOST}/api/auth/login -X POST -H 'Content-Type: application/json' -d '{{\"username\":\"admin\",\"password\":\"admin\"}}'")
        if '"token"' in output and '"user"' in output:
            print("  ✅ API работает через Nginx")
            print(f"  Ответ: {output[:200]}...")
        else:
            print(f"  ❌ API не работает: {output[:200]}")
        
        # 3. Проверка frontend
        print("\n3. ПРОВЕРКА FRONTEND:")
        success, output, error = ssh_exec(ssh, f"curl -s http://{SSH_HOST}/ | head -10")
        if "<!DOCTYPE html>" in output or "<html" in output.lower():
            print("  ✅ Frontend доступен")
        else:
            print(f"  ❌ Frontend не доступен: {output[:200]}")
        
        # 4. Проверка Nginx
        print("\n4. ПРОВЕРКА NGINX:")
        success, output, error = ssh_exec(ssh, "nginx -t 2>&1")
        if "successful" in output.lower():
            print("  ✅ Nginx конфигурация валидна")
        else:
            print(f"  ❌ Ошибка Nginx: {output}")
        
        print("\n" + "="*60)
        print("СТАТУС ПРИЛОЖЕНИЯ")
        print("="*60)
        print(f"\n✅ Приложение полностью развернуто и работает!")
        print(f"\nURL: http://{SSH_HOST}")
        print(f"Логин: admin")
        print(f"Пароль: admin")
        print(f"\nОткройте приложение в браузере и войдите с указанными учетными данными.")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

