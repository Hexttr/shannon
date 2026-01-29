#!/usr/bin/env python3
"""
Исправление base path проблемы
"""

import paramiko
import sys

SSH_HOST = "72.56.79.153"
SSH_USER = "root"
SSH_PASSWORD = "m8J@2_6whwza6U"

def execute_ssh_command(ssh, command, description):
    """Выполняет команду через SSH и выводит результат"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Выполняю: {command}")
    
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    
    output = stdout.read().decode('utf-8', errors='replace')
    errors = stderr.read().decode('utf-8', errors='replace')
    
    if output:
        try:
            print(output)
        except UnicodeEncodeError:
            print(output.encode('ascii', 'replace').decode('ascii'))
    if errors:
        try:
            print(f"Ошибки: {errors}", file=sys.stderr)
        except UnicodeEncodeError:
            print(f"Ошибки: {errors.encode('ascii', 'replace').decode('ascii')}", file=sys.stderr)
    
    return exit_status == 0, output

def main():
    print("="*60)
    print("ИСПРАВЛЕНИЕ BASE PATH ПРОБЛЕМЫ")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
        print("Подключение установлено!")
    except Exception as e:
        print(f"Ошибка подключения: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 1. Проверяем vite.config.ts
        print("\n1. Проверяю vite.config.ts...")
        execute_ssh_command(
            ssh,
            "cat /root/shannon/template/vite.config.ts | grep -A 5 'base'",
            "Base path в vite.config.ts"
        )
        
        # 2. Исправляем vite.config.ts - убираем /app/ base path
        print("\n2. Исправляю vite.config.ts...")
        vite_config = """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // В production используем корень /
  const base = '/';

  return {
    plugins: [react()],
    base,
    build: {
      minify: 'esbuild',
      rollupOptions: {
        output: {
          entryFileNames: `assets/[name]-[hash].js`,
          chunkFileNames: `assets/[name]-[hash].js`,
          assetFileNames: `assets/[name]-[hash].[ext]`,
        },
      },
    },
    server: {
      port: 5173,
      host: '0.0.0.0',
      proxy: {
        '/api': {
          target: 'http://72.56.79.153:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\\/api/, ''),
        },
        '/socket.io': {
          target: 'ws://72.56.79.153:8000',
          ws: true,
        },
      },
    },
  };
});
"""
        
        stdin, stdout, stderr = ssh.exec_command(f"cat > /root/shannon/template/vite.config.ts << 'VITE_EOF'\n{vite_config}\nVITE_EOF\n")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("vite.config.ts обновлен!")
        
        # 3. Пересобираем frontend
        print("\n3. Пересобираю frontend...")
        execute_ssh_command(
            ssh,
            "cd /root/shannon/template && rm -rf dist && npm run build 2>&1 | tail -30",
            "Пересборка frontend"
        )
        
        # 4. Проверяем новый index.html
        print("\n4. Проверяю новый index.html...")
        execute_ssh_command(
            ssh,
            "cat /root/shannon/template/dist/index.html",
            "Содержимое нового index.html"
        )
        
        # 5. Копируем обновленный dist
        print("\n5. Копирую обновленный dist...")
        execute_ssh_command(
            ssh,
            "cp -r /root/shannon/template/dist/* /var/www/shannon/ && chown -R www-data:www-data /var/www/shannon && chmod -R 755 /var/www/shannon",
            "Копирование dist"
        )
        
        # 6. Проверяем содержимое скопированного index.html
        print("\n6. Проверяю скопированный index.html...")
        execute_ssh_command(
            ssh,
            "cat /var/www/shannon/index.html",
            "Содержимое index.html в /var/www/shannon"
        )
        
        # 7. Тестируем HTTP запрос
        print("\n7. Тестирую HTTP запрос...")
        execute_ssh_command(
            ssh,
            "curl -s http://localhost/ | head -15",
            "Проверка HTTP ответа"
        )
        
        # 8. Проверяем доступность статических файлов
        print("\n8. Проверяю доступность статических файлов...")
        execute_ssh_command(
            ssh,
            "ls -la /var/www/shannon/assets/ | head -5",
            "Файлы в assets"
        )
        
        execute_ssh_command(
            ssh,
            "curl -s -I http://localhost/assets/$(ls /var/www/shannon/assets/*.js 2>/dev/null | head -1 | xargs basename) | head -5",
            "Проверка доступности JS файла"
        )
        
        # 9. Настраиваем HTTPS если нужно (опционально)
        print("\n9. Проверяю необходимость HTTPS...")
        execute_ssh_command(
            ssh,
            "test -f /etc/nginx/ssl/72.56.79.153.crt && echo 'SSL сертификат найден' || echo 'SSL сертификат не найден - HTTPS не настроен'",
            "Проверка SSL сертификата"
        )
        
        # 10. Финальная проверка
        print("\n10. Финальная проверка...")
        execute_ssh_command(
            ssh,
            "curl -v http://72.56.79.153/ 2>&1 | head -50",
            "Финальная проверка HTTP"
        )
        
        print("\n" + "="*60)
        print("ИСПРАВЛЕНИЕ ЗАВЕРШЕНО")
        print("="*60)
        print(f"\nHTTP: http://{SSH_HOST}/")
        print(f"Backend API: http://{SSH_HOST}/api/")
        print("\nВАЖНО: Используйте HTTP, а не HTTPS!")
        print("HTTPS не настроен на сервере.")
        print("\nПроверьте работу в браузере по адресу: http://72.56.79.153/")
        
    except Exception as e:
        print(f"\nКритическая ошибка: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        ssh.close()
        print("\nСоединение закрыто.")

if __name__ == "__main__":
    main()

