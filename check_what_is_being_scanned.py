#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка что именно сканируется в текущем пентесте
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def check_scan_target():
    """Проверяет что именно сканируется"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 ПРОВЕРКА ЧТО СКАНИРУЕТСЯ")
        print("="*60)
        
        # 1. Информация о пентесте
        print("\n1. Информация о пентесте:")
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$pentest = App\\\\Models\\\\Pentest::orderBy('created_at', 'desc')->first();
if (\$pentest) {
    echo \$pentest->id . PHP_EOL;
    echo \$pentest->target_url . PHP_EOL;
}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        lines = output.strip().split('\n')
        if len(lines) >= 2:
            pentest_id = lines[0]
            target_url = lines[1]
            print(f"   ID: {pentest_id}")
            print(f"   Target URL: {target_url}")
        else:
            print("   ❌ Пентест не найден")
            return False
        
        # 2. Проверяем файлы результатов - что реально сканировалось
        print("\n2. Анализ файлов результатов:")
        report_dir = f"/root/shannon/pentest_reports/{pentest_id}"
        
        # Nmap
        print("\n   📍 Nmap результаты:")
        output, _, _ = conn.execute(f"cat {report_dir}/nmap.txt 2>&1")
        print(output[:500])
        
        # Проверяем что в команде было
        print("\n   🔍 Поиск URL в логах Nmap:")
        output, _, _ = conn.execute(f"grep -i 'tcell\|ananas\|scan\|target' {report_dir}/nmap.txt 2>&1 | head -5")
        print(output)
        
        # Nikto
        print("\n   📍 Nikto результаты:")
        output, _, _ = conn.execute(f"cat {report_dir}/nikto.txt 2>&1")
        print(output[:500])
        
        # Nuclei (если есть)
        print("\n   📍 Nuclei результаты:")
        output, _, _ = conn.execute(f"head -20 {report_dir}/nuclei.txt 2>&1")
        if output.strip() and 'No such file' not in output:
            print(output)
        else:
            print("   Файл пустой или не найден")
        
        # Dirb (если есть)
        print("\n   📍 Dirb результаты:")
        output, _, _ = conn.execute(f"head -20 {report_dir}/dirb.txt 2>&1")
        if output.strip() and 'No such file' not in output:
            print(output)
        else:
            print("   Файл пустой или не найден")
        
        # 3. Проверяем логи - какие команды выполнялись
        print("\n3. Команды из логов пентеста:")
        cmd = f'''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$pentest = App\\\\Models\\\\Pentest::find('{pentest_id}');
if (\$pentest) {{
    \$logs = \$pentest->logs()->where('message', 'like', '%Результат:%')->get(['message']);
    foreach (\$logs as \$log) {{
        \$msg = \$log->message;
        // Извлекаем URL или хост из сообщения
        if (preg_match('/https?:\\\\/\\\\/[^\\\\s]+/', \$msg, \$matches)) {{
            echo 'Найден URL: ' . \$matches[0] . PHP_EOL;
        }}
        if (preg_match('/-h\\\\s+([^\\\\s]+)|-u\\\\s+([^\\\\s]+)/', \$msg, \$matches)) {{
            echo 'Найден параметр: ' . print_r(\$matches, true) . PHP_EOL;
        }}
        echo substr(\$msg, 0, 300) . PHP_EOL . PHP_EOL;
    }}
}}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        # 4. Проверяем код - как формируются команды
        print("\n4. Проверка кода формирования команд:")
        output, _, _ = conn.execute('grep -A 3 "runNmapScan\|runNiktoScan\|runNucleiScan" /root/shannon/backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php | grep -E "targetUrl|parse_url|command" | head -10')
        print(output)
        
        # 5. Проверяем временные файлы - что там было
        print("\n5. Проверка временных файлов (если еще существуют):")
        output, _, _ = conn.execute(f"ls -la /tmp/*{pentest_id}* 2>&1 | head -10")
        print(output)
        
        # 6. Проверяем что реально доступно на сервере
        print("\n6. Проверка доступности целевого хоста с сервера:")
        host = target_url.replace('https://', '').replace('http://', '').split('/')[0]
        print(f"   Проверяем доступность {host}...")
        output, _, code = conn.execute(f"curl -I -m 5 https://{host} 2>&1 | head -5")
        print(f"   Результат curl: {output[:200]}")
        
        print("\n" + "="*60)
        print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_scan_target()

