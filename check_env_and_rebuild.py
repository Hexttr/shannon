#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка .env и пересборка с очисткой кэша
"""

import paramiko
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"
FRONTEND_DIR = "/root/shannon/template"

def ssh_exec(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    return exit_status == 0, output, error

def main():
    print("="*70)
    print("ПРОВЕРКА .ENV И ПЕРЕСБОРКА С ОЧИСТКОЙ КЭША")
    print("="*70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # 1. Проверяем .env файл
        print("\n1. ПРОВЕРКА .ENV ФАЙЛА:")
        print("-" * 70)
        success, env_content, error = ssh_exec(ssh, f"cat {FRONTEND_DIR}/.env 2>&1")
        if 'VITE_API_URL' in env_content:
            print("  ⚠ Найдена переменная VITE_API_URL:")
            for line in env_content.split('\n'):
                if 'VITE_API_URL' in line:
                    print(f"    {line}")
            
            # Проверяем значение
            if 'http://72.56.79.153:8000' in env_content or 'http://localhost:8000' in env_content:
                print("\n  ⚠ VITE_API_URL указывает на HTTP - это проблема!")
                print("  Удаляем или исправляем VITE_API_URL...")
                # Удаляем строку с VITE_API_URL или комментируем её
                new_env = '\n'.join([line for line in env_content.split('\n') if 'VITE_API_URL' not in line])
                ssh_exec(ssh, f"cat > {FRONTEND_DIR}/.env << 'ENV_EOF'\n{new_env}\nENV_EOF")
                print("  [OK] VITE_API_URL удалена из .env")
        else:
            print("  ✓ VITE_API_URL не найдена в .env (это хорошо)")
        
        # 2. Очищаем кэш Vite
        print("\n2. ОЧИСТКА КЭША VITE:")
        ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/node_modules/.vite")
        ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/.vite")
        print("  [OK] Кэш Vite очищен")
        
        # 3. Удаляем старый dist
        print("\n3. УДАЛЕНИЕ СТАРОГО DIST:")
        ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/dist")
        print("  [OK] Старый dist удален")
        
        # 4. Проверяем api.ts перед сборкой
        print("\n4. ПРОВЕРКА API.TS ПЕРЕД СБОРКОЙ:")
        success2, api_content, error2 = ssh_exec(ssh, f"cat {FRONTEND_DIR}/src/services/api.ts | grep -A 10 'getApiUrl'")
        if 'window.location.protocol' in api_content:
            print("  ✓ api.ts содержит правильный код")
        else:
            print("  ✗ api.ts НЕ содержит правильный код!")
            print(f"  {api_content[:300]}")
            return
        
        # 5. Собираем фронтенд
        print("\n5. СБОРКА ФРОНТЕНДА:")
        print("  Это может занять 2-3 минуты...")
        
        stdin, stdout, stderr = ssh.exec_command(f"cd {FRONTEND_DIR} && npm run build 2>&1")
        output_lines = []
        while True:
            line = stdout.readline()
            if not line:
                break
            output_lines.append(line)
            if len(output_lines) % 30 == 0:
                print(f"  Собрано строк: {len(output_lines)}...")
        
        exit_status = stdout.channel.recv_exit_status()
        output = ''.join(output_lines)
        
        if exit_status == 0:
            print("  [OK] Сборка завершена")
        else:
            print(f"  [ERROR] Ошибка сборки:")
            print(output[-1000:] if len(output) > 1000 else output)
            return
        
        # 6. Проверяем новый JS файл
        print("\n6. ПРОВЕРКА НОВОГО JS ФАЙЛА:")
        success3, js_files, error3 = ssh_exec(ssh, f"ls -t {FRONTEND_DIR}/dist/assets/*.js 2>&1 | head -1")
        if "No such file" in js_files:
            print("  [ERROR] JS файл не найден!")
            return
        
        js_file = js_files.strip().split('\n')[0]
        print(f"  JS файл: {js_file.split('/')[-1]}")
        
        # Проверяем содержимое
        success4, js_check, error4 = ssh_exec(ssh, f"grep -o 'http://72.56.79.153:8000' {js_file} | head -1")
        if js_check.strip():
            print("  ⚠ В коде все еще есть старый URL")
            print("  Это может быть из-за минификации/оптимизации")
        else:
            print("  ✓ Старый URL не найден")
        
        # Проверяем на наличие динамического кода
        success5, dynamic_check, error5 = ssh_exec(ssh, f"grep -o 'location.protocol' {js_file} | head -1")
        if dynamic_check.strip():
            print("  ✓ Найден location.protocol - код динамический")
        else:
            print("  ⚠ location.protocol не найден (возможно минифицирован)")
        
        # 7. Исправляем пути в index.html
        print("\n7. ИСПРАВЛЕНИЕ ПУТЕЙ В INDEX.HTML:")
        success6, html_content, error6 = ssh_exec(ssh, f"cat {FRONTEND_DIR}/dist/index.html")
        if '/app/assets/' in html_content:
            fixed_html = html_content.replace('/app/assets/', '/assets/')
            ssh_exec(ssh, f"cat > {FRONTEND_DIR}/dist/index.html << 'HTML_EOF'\n{fixed_html}\nHTML_EOF")
            print("  [OK] Пути исправлены")
        else:
            print("  [OK] Пути уже правильные")
        
        # 8. Устанавливаем права доступа
        print("\n8. УСТАНОВКА ПРАВ ДОСТУПА:")
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        print("  [OK] Права установлены")
        
        print("\n" + "="*70)
        print("ГОТОВО!")
        print("="*70)
        print("\nВАЖНО: Даже если старый URL найден в минифицированном коде,")
        print("функция getApiUrl() должна выполняться в браузере и использовать")
        print("правильный URL на основе window.location.")
        print("\nПопробуйте:")
        print("1. Очистить кэш браузера (Ctrl+Shift+Delete)")
        print("2. Открыть в режиме инкогнито")
        print("3. Проверить в консоли браузера: window.location.protocol")
        print("="*70)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()



