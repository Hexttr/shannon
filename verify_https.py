#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка HTTPS конфигурации
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
    print("ПРОВЕРКА HTTPS КОНФИГУРАЦИИ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверка портов
        print("\n1. ПРОВЕРКА ПОРТОВ:")
        success, output, error = ssh_exec(ssh, "netstat -tlnp | grep -E ':(80|443)' | head -5")
        print(output)
        
        # 2. Проверка сертификата
        print("\n2. ПРОВЕРКА СЕРТИФИКАТА:")
        success, output, error = ssh_exec(ssh, "ls -la /etc/nginx/ssl/ 2>&1 || ls -la /etc/letsencrypt/live/ 2>&1")
        print(output)
        
        # 3. Проверка конфигурации Nginx
        print("\n3. ПРОВЕРКА NGINX:")
        success, output, error = ssh_exec(ssh, "nginx -t 2>&1")
        print(output)
        
        # 4. Тест HTTPS API
        print("\n4. ТЕСТ HTTPS API:")
        success, output, error = ssh_exec(ssh, f"curl -k -s https://{SSH_HOST}/api/auth/login -X POST -H 'Content-Type: application/json' -d '{{\"username\":\"admin\",\"password\":\"admin\"}}' | head -c 300")
        if '"token"' in output:
            print("  ✅ HTTPS API работает")
            print(f"  Ответ: {output[:200]}...")
        else:
            print(f"  ⚠️  Ответ: {output[:200]}")
        
        # 5. Проверка редиректа HTTP -> HTTPS
        print("\n5. ПРОВЕРКА РЕДИРЕКТА:")
        success, output, error = ssh_exec(ssh, f"curl -I http://{SSH_HOST}/ 2>&1 | head -5")
        if "301" in output or "Location: https://" in output:
            print("  ✅ Редирект HTTP -> HTTPS работает")
        else:
            print(f"  ⚠️  Редирект: {output[:200]}")
        
        print("\n" + "="*60)
        print("ПРОВЕРКА ЗАВЕРШЕНА")
        print("="*60)
        print(f"\nПриложение доступно:")
        print(f"  HTTPS: https://{SSH_HOST}")
        print(f"  HTTP: http://{SSH_HOST} (редирект на HTTPS)")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

