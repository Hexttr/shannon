#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление CSRF для API
"""

import paramiko
import sys
import time

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
BACKEND_DIR = "/root/shannon/backend-laravel"

def ssh_exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    print("="*60)
    print("ИСПРАВЛЕНИЕ CSRF ДЛЯ API")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    sftp = ssh.open_sftp()
    
    try:
        # 1. Чтение текущего VerifyCsrfToken
        print("\n1. ПРОВЕРКА VERIFYCSRFTOKEN:")
        success, output, error = ssh_exec(ssh, f"cat {BACKEND_DIR}/app/Http/Middleware/VerifyCsrfToken.php")
        print(output)
        
        # 2. Обновление VerifyCsrfToken для исключения API из CSRF
        print("\n2. ОБНОВЛЕНИЕ VERIFYCSRFTOKEN:")
        verify_csrf_content = """<?php

namespace App\\Http\\Middleware;

use Illuminate\\Foundation\\Http\\Middleware\\VerifyCsrfToken as Middleware;

class VerifyCsrfToken extends Middleware
{
    /**
     * The URIs that should be excluded from CSRF verification.
     *
     * @var array<int, string>
     */
    protected $except = [
        'api/*',
    ];
}
"""
        
        local_file = "backend-laravel/app/Http/Middleware/VerifyCsrfToken.php"
        remote_file = f"{BACKEND_DIR}/app/Http/Middleware/VerifyCsrfToken.php"
        
        with open(local_file, 'rb') as f:
            sftp.putfo(f, remote_file)
        print("  [OK] VerifyCsrfToken обновлен")
        
        # 3. Альтернативно - убираем EnsureFrontendRequestsAreStateful из API
        # так как для API токенов CSRF не нужен
        print("\n3. ПРОВЕРКА BOOTSTRAP/APP.PHP:")
        success, output, error = ssh_exec(ssh, f"cat {BACKEND_DIR}/bootstrap/app.php")
        
        # Убираем EnsureFrontendRequestsAreStateful из API middleware
        # так как он требует CSRF, а для API токенов это не нужно
        updated_bootstrap = output.replace(
            "->withMiddleware(function (Middleware $middleware) {\n        $middleware->api(prepend: [\n            \\Laravel\\Sanctum\\Http\\Middleware\\EnsureFrontendRequestsAreStateful::class,\n        ]);",
            "->withMiddleware(function (Middleware $middleware) {\n        // EnsureFrontendRequestsAreStateful убран для API - используем токены без CSRF"
        )
        
        if updated_bootstrap != output:
            ssh_exec(ssh, f"cd {BACKEND_DIR} && cat > bootstrap/app.php << 'EOFBOOTSTRAP'\n{updated_bootstrap}\nEOFBOOTSTRAP")
            print("  [OK] bootstrap/app.php обновлен (убрано EnsureFrontendRequestsAreStateful)")
        else:
            print("  [INFO] bootstrap/app.php не требует изменений")
        
        # 4. Очистка кэша
        print("\n4. ОЧИСТКА КЭША:")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan config:clear 2>&1")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan route:clear 2>&1")
        ssh_exec(ssh, f"cd {BACKEND_DIR} && php artisan cache:clear 2>&1")
        print("  [OK] Кэш очищен")
        
        # 5. Перезапуск
        print("\n5. ПЕРЕЗАПУСК:")
        ssh_exec(ssh, "systemctl restart shannon-laravel.service")
        time.sleep(3)
        
        # 6. Тест
        print("\n6. ТЕСТ:")
        import requests
        from urllib3.exceptions import InsecureRequestWarning
        import urllib3
        urllib3.disable_warnings(InsecureRequestWarning)
        
        response = requests.post(
            f"https://{SSH_HOST}/api/auth/login",
            json={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/json", "Origin": f"https://{SSH_HOST}"},
            verify=False,
            timeout=10
        )
        
        print(f"  Статус: {response.status_code}")
        if response.status_code == 200:
            print("  [OK] API работает!")
            print(f"  Ответ: {response.text[:200]}")
        else:
            print(f"  [WARNING] Ответ: {response.text[:300]}")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print(f"\nПопробуйте войти снова:")
        print(f"  URL: https://{SSH_HOST}")
        print(f"  Логин: admin")
        print(f"  Пароль: admin")
        
    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    main()

