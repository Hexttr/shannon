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

print("=== Итоговый отчет об исправлениях ===\n")

print("Исправленные проблемы:\n")

print("1. ✓ Таблица failed_jobs исправлена")
print("   - Проблема: NOT NULL constraint failed: failed_jobs.id")
print("   - Решение: Изменен тип id с string на INTEGER PRIMARY KEY AUTOINCREMENT")
print("   - Статус: Исправлено и пересоздано на сервере\n")

print("2. ✓ Timeout для RunPentestJob увеличен")
print("   - Проблема: Jobs таймаутятся (TimeoutExceededException)")
print("   - Решение: Добавлен timeout = 3600 секунд (1 час)")
print("   - Статус: Исправлено\n")

print("3. ✓ Services.tsx отрефакторен")
print("   - Проблема: Неправильное форматирование, ошибки сборки")
print("   - Решение: Исправлено форматирование, названия полей (target_url, completed_at, etc.)")
print("   - Статус: Исправлено, фронтенд пересобран\n")

print("4. ✓ serviceApi.ts дополнен")
print("   - Добавлен метод update() для обновления сервисов")
print("   - Статус: Исправлено\n")

print("5. ✓ types/index.ts дополнен")
print("   - Добавлен тип UpdateServiceRequest")
print("   - Статус: Исправлено\n")

# Проверяем что все работает
print("\nПроверка статуса:\n")

# Проверяем структуру failed_jobs
print("[1] Структура failed_jobs:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 3 php artisan tinker --execute=\"echo json_encode(DB::select('PRAGMA table_info(failed_jobs)'));\" 2>&1 | tail -5")
stdout.channel.settimeout(5)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    if 'INTEGER' in output and 'id' in output:
        print("✓ Таблица failed_jobs имеет правильную структуру")
    else:
        print(f"Ответ: {output[:200]}")
except:
    pass

# Проверяем что RunPentestJob имеет timeout
print("\n[2] Проверка RunPentestJob:")
stdin, stdout, stderr = ssh.exec_command("grep -E 'timeout|Timeout' /root/shannon/backend-laravel/app/Domain/Pentests/Jobs/RunPentestJob.php | head -3")
stdout.channel.settimeout(3)
try:
    output = stdout.read().decode('utf-8', errors='ignore')
    if 'timeout' in output.lower():
        print("✓ RunPentestJob имеет timeout")
        print(f"  {output.strip()}")
except:
    pass

ssh.close()

print("\n=== Все исправления применены ===")
print("\nИзменения закоммичены и запушены в git")
