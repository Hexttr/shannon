#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import paramiko

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("72.56.79.153", port=22, username="root", password="m8J@2_6whwza6U", timeout=10)

print("=== Загрузка исправлений и push в git ===\n")

# Загружаем исправленный RunPentestJob
print("[1] Загрузка исправленного RunPentestJob...")
sftp = ssh.open_sftp()
with open("backend-laravel/app/Domain/Pentests/Jobs/RunPentestJob.php", 'r', encoding='utf-8') as f:
    content = f.read()
with sftp.file("/root/shannon/backend-laravel/app/Domain/Pentests/Jobs/RunPentestJob.php", 'w') as rf:
    rf.write(content.encode('utf-8'))
sftp.close()
print("✓ RunPentestJob загружен")

# Перезапускаем queue worker
print("\n[2] Перезапуск queue worker...")
ssh.exec_command("systemctl restart shannon-queue.service")
print("✓ Queue worker перезапущен")

# Коммитим и пушим изменения
print("\n[3] Коммит и push в git...")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon && git add -A && git status --short")
stdout.channel.settimeout(5)
try:
    status = stdout.read().decode('utf-8', errors='ignore')
    if status.strip():
        print("Измененные файлы:")
        print(status)
        
        # Коммитим
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon && git commit -m 'Fix failed_jobs table and increase job timeout'")
        stdout.channel.settimeout(5)
        commit_output = stdout.read().decode('utf-8', errors='ignore')
        print(f"\nКоммит: {commit_output.strip()}")
        
        # Пушим
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon && git push origin master")
        stdout.channel.settimeout(10)
        push_output = stdout.read().decode('utf-8', errors='ignore')
        print(f"\nPush: {push_output.strip()}")
    else:
        print("Нет изменений для коммита")
except:
    pass

ssh.close()
print("\n=== Готово ===")


