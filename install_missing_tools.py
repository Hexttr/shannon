#!/usr/bin/env python3
"""
Установка недостающих инструментов
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
    
    if error_output:
        try:
            print(f"ERROR: {error_output[:500]}")
        except:
            print(f"ERROR: {error_output[:500].encode('ascii', 'replace').decode('ascii')}")
    
    return exit_status == 0

def main():
    print("="*60)
    print("УСТАНОВКА НЕДОСТАЮЩИХ ИНСТРУМЕНТОВ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Установка Nuclei
        print("\n1. Установка Nuclei...")
        execute_command(ssh, "which nuclei", "Проверка наличия nuclei")
        if not execute_command(ssh, "which nuclei", "Проверка наличия nuclei"):
            execute_command(ssh, 
                "cd /tmp && wget -q https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_3.2.7_linux_amd64.zip && unzip -q nuclei_3.2.7_linux_amd64.zip && mv nuclei /usr/local/bin/ && chmod +x /usr/local/bin/nuclei && rm nuclei_3.2.7_linux_amd64.zip",
                "Установка Nuclei"
            )
            execute_command(ssh, "nuclei -version", "Проверка версии Nuclei")
        
        # 2. Установка WPScan (через Ruby gem)
        print("\n2. Установка WPScan...")
        if not execute_command(ssh, "which wpscan", "Проверка наличия wpscan"):
            execute_command(ssh, "apt-get install -y ruby ruby-dev build-essential", "Установка Ruby")
            execute_command(ssh, "gem install wpscan", "Установка WPScan через gem")
            execute_command(ssh, "wpscan --version", "Проверка версии WPScan")
        
        # 3. Установка Subfinder
        print("\n3. Установка Subfinder...")
        if not execute_command(ssh, "which subfinder", "Проверка наличия subfinder"):
            execute_command(ssh,
                "cd /tmp && wget -q https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_2.6.7_linux_amd64.zip && unzip -q subfinder_2.6.7_linux_amd64.zip && mv subfinder /usr/local/bin/ && chmod +x /usr/local/bin/subfinder && rm subfinder_2.6.7_linux_amd64.zip",
                "Установка Subfinder"
            )
            execute_command(ssh, "subfinder -version", "Проверка версии Subfinder")
        
        # Финальная проверка
        print("\n" + "="*60)
        print("ФИНАЛЬНАЯ ПРОВЕРКА")
        print("="*60)
        
        tools = ["nmap", "nikto", "sqlmap", "nuclei", "dirb", "gobuster", "wpscan", "whatweb", "subfinder", "httpx"]
        for tool in tools:
            stdin, stdout, stderr = ssh.exec_command(f"which {tool}")
            if stdout.channel.recv_exit_status() == 0:
                print(f"[OK] {tool}")
            else:
                print(f"[ERROR] {tool}")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

