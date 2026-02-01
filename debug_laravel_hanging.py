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

print("=== Отладка зависания Laravel ===\n")

# Проверка что Laravel отвечает быстро
print("[1] Тест быстрого ответа Laravel:")
stdin, stdout, stderr = ssh.exec_command("timeout 2 curl -s http://localhost:8000/up || echo 'TIMEOUT'")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"Ответ: {output}")
except:
    print("Таймаут")

# Проверка логов Laravel на медленные запросы
print("\n[2] Медленные запросы в логах:")
stdin, stdout, stderr = ssh.exec_command("tail -100 /root/shannon/backend-laravel/storage/logs/laravel.log | grep -E 'slow|Slow|SLOW|took|duration' | tail -5")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output if output else "Нет информации о медленных запросах")
except:
    pass

# Проверка блокировок базы данных
print("\n[3] Проверка блокировок БД:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"try { DB::select('SELECT 1'); echo 'OK'; } catch (Exception \$e) { echo 'ERROR: ' . \$e->getMessage(); }\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    print(output)
except:
    print("Таймаут")

# Перезапуск Laravel для очистки состояния
print("\n[4] Перезапуск Laravel...")
stdin, stdout, stderr = ssh.exec_command("systemctl restart shannon-laravel.service")
stdout.channel.settimeout(3)
stdout.read()
print("✓ Перезапущен")

# Ждем запуска
import time
time.sleep(3)

# Тест после перезапуска
print("\n[5] Тест API после перезапуска:")
stdin, stdout, stderr = ssh.exec_command("timeout 5 curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' | head -3")
stdout.channel.settimeout(6)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if 'token' in output:
        print("✓ API работает!")
    else:
        print(f"Ответ: {output[:200]}")
except:
    print("Таймаут")

ssh.close()


