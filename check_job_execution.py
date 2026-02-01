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

print("=== Проверка выполнения Job ===\n")

# Проверяем очередь
print("[1] Проверка очереди:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo DB::table('jobs')->count();\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    job_count = output.split('\n')[-1] if '\n' in output else output
    print(f"Заданий в очереди: {job_count}")
except:
    pass

# Проверяем failed jobs
print("\n[2] Проверка failed jobs:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo DB::table('failed_jobs')->count();\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    failed_count = output.split('\n')[-1] if '\n' in output else output
    print(f"Неудачных заданий: {failed_count}")
    if int(failed_count) > 0:
        print("✗ Есть failed jobs - проверьте логи")
except:
    pass

# Проверяем логи queue worker
print("\n[3] Логи queue worker:")
stdin, stdout, stderr = ssh.exec_command("journalctl -u shannon-queue.service -n 20 --no-pager | tail -15")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    if output.strip():
        print(output)
    else:
        print("Нет логов")
except:
    pass

# Проверяем последние ошибки Laravel
print("\n[4] Последние ошибки Laravel:")
stdin, stdout, stderr = ssh.exec_command("tail -50 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'ERROR|Exception|RunPentestJob|addLog' | tail -10")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if output:
        print(output)
    else:
        print("Нет ошибок")
except:
    pass

ssh.close()

