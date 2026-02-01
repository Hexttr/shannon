#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление AuthContext для предотвращения застревания в loading
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
    print("="*60)
    print("ИСПРАВЛЕНИЕ AUTHCONTEXT")
    print("="*60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Читаем текущий AuthContext
        print("\n1. ЧТЕНИЕ AUTHCONTEXT:")
        success, content, error = ssh_exec(ssh, f"cat {FRONTEND_DIR}/src/contexts/AuthContext.tsx")
        if not success:
            print(f"  [ERROR] Не удалось прочитать файл: {error}")
            return
        
        print(f"  [OK] Файл прочитан ({len(content)} байт)")
        
        # Проверяем, есть ли finally блок
        if "} finally {" in content or "} finally {" in content:
            print("  [OK] finally блок уже есть")
        else:
            # Исправляем checkAuth функцию
            print("\n2. ИСПРАВЛЕНИЕ CHECKAUTH:")
            # Ищем функцию checkAuth и добавляем finally блок
            import re
            
            # Паттерн для поиска функции checkAuth
            pattern = r'(const checkAuth = async \(\) => \{.*?setIsLoading\(false\);.*?\n  \};)'
            
            # Новая версия с finally
            new_checkAuth = '''  const checkAuth = async () => {
    window.__DEBUG__?.log('[AuthContext] Проверка токена при загрузке...');
    const token = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('user');
    window.__DEBUG__?.log('[AuthContext] Токен в localStorage:', token ? 'найден' : 'не найден');
    window.__DEBUG__?.log('[AuthContext] Пользователь в localStorage:', savedUser ? 'найден' : 'не найден');

    if (token && savedUser) {
      try {
        window.__DEBUG__?.log('[AuthContext] Проверка токена через API...');
        const response = await authApi.getMe();
        window.__DEBUG__?.log('[AuthContext] Токен валиден, пользователь:', response.data);
        setUser(response.data);
      } catch (error: any) {
        window.__DEBUG__?.log('[AuthContext] Токен невалиден или ошибка API:', error.response?.status, error.response?.data);
        // Токен невалиден или ошибка API, очищаем
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        setUser(null);
      } finally {
        // Всегда устанавливаем isLoading в false, даже при ошибке
        setIsLoading(false);
      }
    } else {
      window.__DEBUG__?.log('[AuthContext] Токен не найден, устанавливаем isLoading=false');
      setIsLoading(false);
    }
  };'''
            
            # Заменяем функцию
            new_content = re.sub(
                r'const checkAuth = async \(\) => \{.*?setIsLoading\(false\);.*?\n  \};',
                new_checkAuth,
                content,
                flags=re.DOTALL
            )
            
            if new_content != content:
                # Записываем обратно
                ssh_exec(ssh, f"cat > {FRONTEND_DIR}/src/contexts/AuthContext.tsx << 'AUTH_EOF'\n{new_content}\nAUTH_EOF")
                print("  [OK] AuthContext исправлен")
            else:
                print("  [WARNING] Не удалось найти функцию для замены")
        
        print("\n" + "="*60)
        print("ГОТОВО!")
        print("="*60)
        print("\nТеперь нужно пересобрать фронтенд для применения изменений.")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()


