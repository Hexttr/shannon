#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ручное исправление форматирования Pentests.tsx
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
    print("РУЧНОЕ ИСПРАВЛЕНИЕ ФОРМАТИРОВАНИЯ")
    print("="*70)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    
    try:
        # Читаем локальный файл
        print("\n1. ЧТЕНИЕ ЛОКАЛЬНОГО ФАЙЛА:")
        print("-" * 70)
        try:
            with open('template/src/pages/Pentests.tsx', 'r', encoding='utf-8') as f:
                local_content = f.read()
            print(f"  [OK] Файл прочитан ({len(local_content)} символов)")
        except Exception as e:
            print(f"  [ERROR] Ошибка чтения: {e}")
            return
        
        # Исправляем проблемные места вручную
        print("\n2. ИСПРАВЛЕНИЕ ПРОБЛЕМНЫХ МЕСТ:")
        print("-" * 70)
        
        # Исправляем return statement - добавляем перенос строки
        fixed_content = local_content.replace(
            'return (    <div className={`bg-gradient-to-br',
            'return (\n    <div className={`bg-gradient-to-br'
        )
        
        # Исправляем закрывающие скобки JSX
        fixed_content = fixed_content.replace(
            '    </div>\n    );',
            '    </div>\n  );'
        )
        
        # Исправляем сжатые useQuery в функции Pentests
        fixed_content = fixed_content.replace(
            '  });  // Фильтруем пентесты по выбранному сервису для метрик  const filteredPentestsForMetrics = useMemo(() => {',
            '  });\n\n  // Фильтруем пентесты по выбранному сервису для метрик\n  const filteredPentestsForMetrics = useMemo(() => {'
        )
        
        # Исправляем сжатые useMemo
        fixed_content = fixed_content.replace(
            '  }, [filteredPentestsForMetrics]);  // Фильтруем и группируем пентесты  const { filteredAndGroupedPentests, groupedByService } = useMemo(() => {',
            '  }, [filteredPentestsForMetrics]);\n\n  // Фильтруем и группируем пентесты\n  const { filteredAndGroupedPentests, groupedByService } = useMemo(() => {'
        )
        
        # Исправляем сжатые функции
        fixed_content = fixed_content.replace(
            '  }, [pentests, services, selectedServiceId, statusFilter, searchQuery]);  // Вычисляем длительность пентеста  const getDuration = (pentest: Pentest): string => {',
            '  }, [pentests, services, selectedServiceId, statusFilter, searchQuery]);\n\n  // Вычисляем длительность пентеста\n  const getDuration = (pentest: Pentest): string => {'
        )
        
        # Исправляем сжатые mutations
        fixed_content = fixed_content.replace(
            '    } catch (error) {      console.error(`[Pentests] Ошибка расчета длительности:`, error);      return \'-\';    }  };  const createAndStartMutation = useMutation({',
            '    } catch (error) {\n      console.error(`[Pentests] Ошибка расчета длительности:`, error);\n      return \'-\';\n    }\n  };\n\n  const createAndStartMutation = useMutation({'
        )
        
        # Исправляем сжатые функции getStatus
        fixed_content = fixed_content.replace(
            '  });  const getStatusColor = (status: Pentest[\'status\']) => {',
            '  });\n\n  const getStatusColor = (status: Pentest[\'status\']) => {'
        )
        
        fixed_content = fixed_content.replace(
            '  };  const getStatusText = (status: Pentest[\'status\']) => {',
            '  };\n\n  const getStatusText = (status: Pentest[\'status\']) => {'
        )
        
        fixed_content = fixed_content.replace(
            '  };  const handleStartPentest = () => {',
            '  };\n\n  const handleStartPentest = () => {'
        )
        
        fixed_content = fixed_content.replace(
            '    });  };  return (',
            '    });\n  };\n\n  return ('
        )
        
        # Загружаем исправленный файл
        print("\n3. ЗАГРУЗКА ИСПРАВЛЕННОГО ФАЙЛА:")
        print("-" * 70)
        sftp = ssh.open_sftp()
        try:
            with sftp.file(f'{FRONTEND_DIR}/src/pages/Pentests.tsx', 'w') as remote_file:
                remote_file.write(fixed_content)
            print("  [OK] Файл загружен")
        except Exception as e:
            print(f"  [ERROR] Ошибка загрузки: {e}")
            sftp.close()
            return
        sftp.close()
        
        # Пересобираем фронтенд
        print("\n4. ПЕРЕСБОРКА ФРОНТЕНДА:")
        print("-" * 70)
        ssh_exec(ssh, f"rm -rf {FRONTEND_DIR}/dist")
        print("  [OK] Старый dist удален")
        
        print("  Запускаем сборку (это может занять 2-3 минуты)...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {FRONTEND_DIR} && npm run build 2>&1")
        output_lines = []
        error_lines = []
        
        while True:
            line = stdout.readline()
            if not line:
                break
            output_lines.append(line)
            if len(output_lines) % 30 == 0:
                print(f"  Собрано строк: {len(output_lines)}...")
        
        while True:
            line = stderr.readline()
            if not line:
                break
            error_lines.append(line)
        
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("  [OK] Сборка завершена")
        else:
            print(f"  [ERROR] Ошибка сборки")
            output = ''.join(output_lines)
            errors = ''.join(error_lines)
            print(output[-1500:] if len(output) > 1500 else output)
            if errors:
                print("\n  Ошибки:")
                print(errors[-500:] if len(errors) > 500 else errors)
            return
        
        # Исправляем пути в index.html
        print("\n5. ИСПРАВЛЕНИЕ ПУТЕЙ В INDEX.HTML:")
        print("-" * 70)
        success5, html_content, error5 = ssh_exec(ssh, f"cat {FRONTEND_DIR}/dist/index.html")
        if '/app/assets/' in html_content:
            fixed_html = html_content.replace('/app/assets/', '/assets/')
            ssh_exec(ssh, f"cat > {FRONTEND_DIR}/dist/index.html << 'HTML_EOF'\n{fixed_html}\nHTML_EOF")
            print("  [OK] Пути исправлены")
        else:
            print("  [OK] Пути уже правильные")
        
        # Устанавливаем права доступа
        print("\n6. УСТАНОВКА ПРАВ ДОСТУПА:")
        print("-" * 70)
        ssh_exec(ssh, f"chown -R www-data:www-data {FRONTEND_DIR}/dist")
        ssh_exec(ssh, f"chmod -R 755 {FRONTEND_DIR}/dist")
        print("  [OK] Права установлены")
        
        print("\n" + "="*70)
        print("ГОТОВО!")
        print("="*70)
        print("\nПопробуйте обновить страницу (Ctrl+F5) и проверить снова.")
        print("="*70)
        
    finally:
        ssh.close()

if __name__ == "__main__":
    main()


