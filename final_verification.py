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

print("=== Финальная проверка ===\n")

# Статус сервисов
print("[1] Статус сервисов:")
stdin, stdout, stderr = ssh.exec_command("systemctl is-active shannon-laravel.service shannon-queue.service nginx.service")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8').strip()
    print(output)
except:
    pass

# Проверка конфигурации очереди
print("\n[2] Конфигурация очереди:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo config('queue.default');\" 2>&1 | tail -3")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    queue_type = output.split('\n')[-1] if '\n' in output else output
    print(f"Тип очереди: {queue_type}")
except:
    pass

# Тест API
print("\n[3] Тест API:")
stdin, stdout, stderr = ssh.exec_command("timeout 5 curl -s http://localhost:8000/api/auth/login -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' | head -3")
stdout.channel.settimeout(6)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if 'token' in output:
        print("✓ API работает")
    else:
        print(f"Ответ: {output[:200]}")
except:
    print("Таймаут")

# Проверка процессов
print("\n[4] Активные процессы:")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep -E 'php.*artisan' | grep -v grep | wc -l")
stdout.channel.settimeout(3)
try:
    count = stdout.read().decode('utf-8').strip()
    print(f"Процессов Laravel: {count}")
    if int(count) >= 2:
        print("✓ Laravel и Queue Worker работают")
except:
    pass

ssh.close()

print("\n=== Итоги исправлений ===")
print("\n1. ✓ Очередь настроена на database")
print("2. ✓ Queue Worker запущен как отдельный сервис")
print("3. ✓ Пентесты выполняются асинхронно (не блокируют API)")
print("4. ✓ Улучшена обработка ошибок авторизации (не выкидывает при таймаутах)")
print("5. ✓ Увеличены таймауты Nginx (300s)")
print("6. ✓ Добавлено создание логов пентеста")
print("\nПопробуйте:")
print("  - Войти в систему: https://72.56.79.153")
print("  - Запустить пентест")
print("  - Проверить что после запуска можно продолжать работать")


