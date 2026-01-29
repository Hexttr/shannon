#!/usr/bin/env python3
"""
Исправление установки nuclei и subfinder
"""

import paramiko
import sys

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def execute_command(ssh, command, description):
    """Выполняет команду и возвращает результат"""
    print(f"\n{description}")
    stdin, stdout, stderr = ssh.exec_command(command, timeout=600)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error_output = stderr.read().decode('utf-8', errors='replace')
    
    if output:
        try:
            print(output[:800])
        except:
            print(output[:800].encode('ascii', 'replace').decode('ascii'))
    
    if error_output and exit_status != 0:
        try:
            print(f"ERROR: {error_output[:500]}")
        except:
            print(f"ERROR: {error_output[:500].encode('ascii', 'replace').decode('ascii')}")
    
    return exit_status == 0

def main():
    print("="*60)
    print("ИСПРАВЛЕНИЕ УСТАНОВКИ NUCLEI И SUBFINDER")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Установка Nuclei (правильная версия)
        print("\n1. Установка Nuclei...")
        stdin, stdout, stderr = ssh.exec_command("which nuclei")
        if stdout.channel.recv_exit_status() != 0:
            # Скачиваем правильную версию
            execute_command(ssh,
                "cd /tmp && wget -q https://github.com/projectdiscovery/nuclei/releases/download/v3.2.7/nuclei_3.2.7_linux_amd64.zip -O /tmp/nuclei.zip && unzip -q -o /tmp/nuclei.zip && mv nuclei /usr/local/bin/ && chmod +x /usr/local/bin/nuclei && rm /tmp/nuclei.zip",
                "Установка Nuclei"
            )
            execute_command(ssh, "nuclei -version", "Проверка Nuclei")
        
        # 2. Установка Subfinder (правильная версия)
        print("\n2. Установка Subfinder...")
        stdin, stdout, stderr = ssh.exec_command("which subfinder")
        if stdout.channel.recv_exit_status() != 0:
            execute_command(ssh,
                "cd /tmp && wget -q https://github.com/projectdiscovery/subfinder/releases/download/v2.6.7/subfinder_2.6.7_linux_amd64.zip -O /tmp/subfinder.zip && unzip -q -o /tmp/subfinder.zip && mv subfinder /usr/local/bin/ && chmod +x /usr/local/bin/subfinder && rm /tmp/subfinder.zip",
                "Установка Subfinder"
            )
            execute_command(ssh, "subfinder -version", "Проверка Subfinder")
        
        # Финальная проверка
        print("\n" + "="*60)
        print("ФИНАЛЬНАЯ ПРОВЕРКА")
        print("="*60)
        
        tools = ["nuclei", "subfinder"]
        for tool in tools:
            stdin, stdout, stderr = ssh.exec_command(f"which {tool}")
            if stdout.channel.recv_exit_status() == 0:
                print(f"[OK] {tool} установлен")
                # Проверяем версию
                stdin, stdout, stderr = ssh.exec_command(f"{tool} -version 2>&1 | head -1")
                version = stdout.read().decode('utf-8', errors='replace').strip()
                print(f"    Версия: {version}")
            else:
                print(f"[ERROR] {tool} не установлен")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

