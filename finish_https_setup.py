#!/usr/bin/env python3
"""
Завершение настройки HTTPS
"""

import paramiko
import sys
import time

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
            print(output[:500])
        except:
            print(output[:500].encode('ascii', 'replace').decode('ascii'))
    return exit_status == 0, output

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Обновляем CORS
        print("Обновляю CORS...")
        stdin, stdout, stderr = ssh.exec_command("cat /root/shannon/backend/.env")
        env_content = stdout.read().decode('utf-8', errors='replace')
        lines = env_content.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith('CORS_ORIGINS='):
                new_lines.append('CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://72.56.79.153","https://72.56.79.153"]')
            else:
                new_lines.append(line)
        new_env = '\n'.join(new_lines)
        ssh.exec_command(f"cat > /root/shannon/backend/.env << 'EOF'\n{new_env}\nEOF\n")
        
        # Обновляем frontend .env
        print("Обновляю frontend .env...")
        frontend_env = "VITE_API_URL=https://72.56.79.153/api\nVITE_WS_URL=https://72.56.79.153\n"
        ssh.exec_command(f"cat > /root/shannon/template/.env << 'EOF'\n{frontend_env}\nEOF\n")
        
        # Перезапускаем backend
        print("Перезапускаю backend...")
        ssh.exec_command("pkill -f 'python.*uvicorn.*app.main:socketio_app' || true")
        time.sleep(2)
        ssh.exec_command("cd /root/shannon/backend && python3 -m uvicorn app.main:socketio_app --host 0.0.0.0 --port 8000 > /tmp/shannon-backend.log 2>&1 &")
        time.sleep(3)
        
        # Пересобираем frontend
        print("Пересобираю frontend...")
        execute_ssh_command(ssh, "cd /root/shannon/template && npm run build 2>&1 | tail -10", "Сборка")
        
        # Копируем dist
        print("Копирую dist...")
        ssh.exec_command("cp -r /root/shannon/template/dist/* /var/www/shannon/ && chown -R www-data:www-data /var/www/shannon")
        
        print("\nГотово! SSL настроен.")
        print(f"HTTPS: https://{SSH_HOST}/")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

