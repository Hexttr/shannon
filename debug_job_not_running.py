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

print("=== Отладка почему Job не выполняется ===\n")

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
        print("\n[3] Детали failed jobs:")
        stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo json_encode(DB::table('failed_jobs')->latest('failed_at')->first(['exception', 'failed_at']));\" 2>&1 | tail -10")
        stdout.channel.settimeout(5)
        try:
            failed_details = stdout.read().decode('utf-8', errors='ignore')
            print(failed_details)
        except:
            pass
except:
    pass

# Проверяем последние ошибки Laravel
print("\n[4] Последние ошибки Laravel:")
stdin, stdout, stderr = ssh.exec_command("tail -200 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'ERROR|Exception|RunPentestJob|PentestEngine|addLog' | tail -30")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if output:
        print(output)
    else:
        print("Нет ошибок")
except:
    pass

# Проверяем логи queue worker
print("\n[5] Логи queue worker:")
stdin, stdout, stderr = ssh.exec_command("journalctl -u shannon-queue.service -n 50 --no-pager | grep -E 'ERROR|Exception|Processing|Processed' | tail -20")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    if output.strip():
        print(output)
    else:
        print("Нет логов обработки")
except:
    pass

# Тестируем выполнение Job вручную
print("\n[6] Тест выполнения Job вручную:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 5 php artisan queue:work database --once --verbose 2>&1 | head -20")
stdout.channel.settimeout(6)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    print(output)
except:
    pass

ssh.close()


