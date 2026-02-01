#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление генерации UUID для Service модели
"""

import paramiko
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def ssh_exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    print("="*70)
    print("ИСПРАВЛЕНИЕ ГЕНЕРАЦИИ UUID ДЛЯ SERVICE")
    print("="*70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Исправляем CreateServiceAction для генерации UUID
        print("\n1. ИСПРАВЛЕНИЕ CREATE SERVICE ACTION:")
        print("-" * 70)
        
        fixed_action = """<?php

namespace App\\Domain\\Services\\Actions;

use App\\Data\\Services\\CreateServiceData;
use App\\Data\\Services\\ServiceData;
use App\\Models\\Service;
use Illuminate\\Support\\Str;

class CreateServiceAction
{
    public function execute(CreateServiceData $data): ServiceData
    {
        $service = Service::create([
            'id' => Str::uuid()->toString(),
            'name' => $data->name,
            'url' => $data->url,
        ]);

        return ServiceData::from([
            'id' => $service->id,
            'name' => $service->name,
            'url' => $service->url,
            'created_at' => $service->created_at->toISOString(),
            'updated_at' => $service->updated_at->toISOString(),
        ]);
    }
}
"""
        
        ssh_exec(ssh, f"cat > /root/shannon/backend-laravel/app/Domain/Services/Actions/CreateServiceAction.php << 'ACTION_EOF'\n{fixed_action}\nACTION_EOF")
        print("  [OK] CreateServiceAction исправлен")
        
        # Проверяем файл
        success, content, error = ssh_exec(ssh, "cat /root/shannon/backend-laravel/app/Domain/Services/Actions/CreateServiceAction.php")
        if 'Str::uuid()' in content:
            print("  ✓ UUID генерация добавлена")
        else:
            print("  ✗ UUID генерация не найдена")
            print(content)
        
        # Также проверяем и исправляем CreatePentestAction, если нужно
        print("\n2. ПРОВЕРКА CREATE PENTEST ACTION:")
        print("-" * 70)
        success2, pentest_action, error2 = ssh_exec(ssh, "cat /root/shannon/backend-laravel/app/Domain/Pentests/Actions/CreatePentestAction.php")
        if 'Str::uuid()' not in pentest_action:
            print("  ⚠ CreatePentestAction также не генерирует UUID")
            print("  Исправляем...")
            
            fixed_pentest_action = """<?php

namespace App\\Domain\\Pentests\\Actions;

use App\\Data\\Pentests\\CreatePentestData;
use App\\Data\\Pentests\\PentestData;
use App\\Models\\Pentest;
use Illuminate\\Support\\Str;

class CreatePentestAction
{
    public function execute(CreatePentestData $data): PentestData
    {
        $pentest = Pentest::create([
            'id' => Str::uuid()->toString(),
            'name' => $data->name,
            'target_url' => $data->config->target_url,
            'status' => 'pending',
            'config' => $data->config->toArray(),
        ]);

        return PentestData::from([
            'id' => $pentest->id,
            'name' => $pentest->name,
            'target_url' => $pentest->target_url,
            'status' => $pentest->status,
            'current_step' => $pentest->current_step,
            'step_progress' => $pentest->step_progress,
            'created_at' => $pentest->created_at->toISOString(),
            'started_at' => $pentest->started_at?->toISOString(),
            'completed_at' => $pentest->completed_at?->toISOString(),
        ]);
    }
}
"""
            ssh_exec(ssh, f"cat > /root/shannon/backend-laravel/app/Domain/Pentests/Actions/CreatePentestAction.php << 'PENTEST_ACTION_EOF'\n{fixed_pentest_action}\nPENTEST_ACTION_EOF")
            print("  [OK] CreatePentestAction исправлен")
        else:
            print("  ✓ CreatePentestAction уже генерирует UUID")
        
        # Тестируем создание сервиса
        print("\n3. ТЕСТИРОВАНИЕ СОЗДАНИЯ СЕРВИСА:")
        print("-" * 70)
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        try:
            # Логинимся
            login_response = requests.post(
                "https://72.56.79.153/api/auth/login",
                json={"username": "admin", "password": "admin"},
                verify=False,
                timeout=5
            )
            
            if login_response.status_code == 200:
                token = login_response.json()['token']
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                # Пробуем создать сервис
                create_response = requests.post(
                    "https://72.56.79.153/api/services",
                    json={"name": "Test Service", "url": "https://example.com"},
                    headers=headers,
                    verify=False,
                    timeout=5
                )
                
                print(f"  Статус: {create_response.status_code}")
                if create_response.status_code == 201:
                    print(f"  ✓ Сервис создан успешно!")
                    print(f"  Ответ: {create_response.json()}")
                else:
                    print(f"  ✗ Ошибка создания сервиса")
                    print(f"  Ответ: {create_response.text[:500]}")
            else:
                print(f"  ✗ Ошибка авторизации: {login_response.status_code}")
        except Exception as e:
            print(f"  ✗ Ошибка тестирования: {str(e)}")
        
        print("\n" + "="*70)
        print("ГОТОВО!")
        print("="*70)
        print("\nТеперь при создании сервиса будет автоматически генерироваться UUID.")
        print("Попробуйте создать сервис снова в интерфейсе.")
        print("="*70)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()



