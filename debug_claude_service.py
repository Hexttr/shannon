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

print("=== Отладка ClaudeApiService ===\n")

# Проверяем .env напрямую
print("[1] Проверка .env:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && grep '^CLAUDE_API_KEY=' .env | wc -c")
stdout.channel.settimeout(3)
try:
    key_length = int(stdout.read().decode('utf-8').strip())
    print(f"Длина строки ключа: {key_length} символов")
    if key_length > 50:
        print("✓ Ключ присутствует в .env")
    else:
        print("✗ Ключ слишком короткий или отсутствует")
except:
    pass

# Проверяем через Laravel config
print("\n[2] Проверка через Laravel config:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 5 php artisan tinker --execute=\"\\$key = config('services.claude.api_key'); echo \\$key ? 'KEY_LENGTH: ' . strlen(\\$key) : 'KEY_NULL';\" 2>&1 | tail -5")
stdout.channel.settimeout(6)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    config_check = output.split('\n')[-1] if '\n' in output else output
    print(f"Результат: {config_check}")
    if 'KEY_LENGTH' in config_check:
        length = int(config_check.split(':')[1].strip())
        if length > 50:
            print("✓ Ключ загружен правильно")
        else:
            print("⚠ Ключ слишком короткий")
except:
    pass

# Проверяем код ClaudeApiService
print("\n[3] Проверка кода ClaudeApiService:")
stdin, stdout, stderr = ssh.exec_command("head -20 /root/shannon/backend-laravel/app/Services/ClaudeApiService.php | tail -10")
stdout.channel.settimeout(3)
try:
    code = stdout.read().decode('utf-8', errors='ignore')
    print(code)
    if '?string' in code:
        print("✓ Тип apiKey nullable")
    if 'config(' in code:
        print("✓ Использует config() для загрузки ключа")
except:
    pass

# Тестируем создание ClaudeApiService
print("\n[4] Тест создания ClaudeApiService:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 5 php artisan tinker --execute=\"use App\\Services\\ClaudeApiService; \\$service = app(ClaudeApiService::class); echo 'SERVICE_CREATED';\" 2>&1 | tail -5")
stdout.channel.settimeout(6)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    if 'SERVICE_CREATED' in output:
        print("✓ Сервис создается без ошибок")
    else:
        print(f"Ответ: {output}")
except:
    pass

# Проверяем env() напрямую
print("\n[5] Проверка env() напрямую:")
stdin, stdout, stderr = ssh.exec_command("cd /root/shannon/backend-laravel && timeout 5 php artisan tinker --execute=\"echo env('CLAUDE_API_KEY') ? 'ENV_KEY_EXISTS' : 'ENV_KEY_NOT_FOUND';\" 2>&1 | tail -5")
stdout.channel.settimeout(6)
try:
    output = stdout.read().decode('utf-8', errors='ignore').strip()
    env_check = output.split('\n')[-1] if '\n' in output else output
    print(f"Результат: {env_check}")
except:
    pass

ssh.close()

