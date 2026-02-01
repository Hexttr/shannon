#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка отображения уязвимостей и копирование результатов
"""

import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection
import base64

def check_and_copy():
    """Проверяет уязвимости и копирует результаты"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔍 ПРОВЕРКА УЯЗВИМОСТЕЙ И КОПИРОВАНИЕ РЕЗУЛЬТАТОВ")
        print("="*60)
        
        # 1. Находим последний пентест
        print("\n1. Поиск последнего пентеста...")
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$pentest = App\\\\Models\\\\Pentest::orderBy('created_at', 'desc')->first();
if (\$pentest) {
    echo \$pentest->id . PHP_EOL;
    echo \$pentest->target_url . PHP_EOL;
    echo \$pentest->status . PHP_EOL;
}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        lines = output.strip().split('\n')
        if len(lines) >= 3:
            pentest_id = lines[0]
            target_url = lines[1]
            status = lines[2]
            print(f"   ID: {pentest_id}")
            print(f"   URL: {target_url}")
            print(f"   Status: {status}")
        else:
            print("   ❌ Пентест не найден")
            return False
        
        # 2. Проверяем уязвимости в БД
        print("\n2. Проверка уязвимостей в БД:")
        cmd = f'''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$pentest = App\\\\Models\\\\Pentest::find('{pentest_id}');
if (\$pentest) {{
    \$vulns = \$pentest->vulnerabilities()->get(['id', 'title', 'description', 'severity', 'cvss_score', 'cve', 'created_at']);
    echo 'Всего уязвимостей: ' . \$vulns->count() . PHP_EOL;
    foreach (\$vulns as \$v) {{
        echo PHP_EOL . 'ID: ' . \$v->id . PHP_EOL;
        echo 'Title: ' . \$v->title . PHP_EOL;
        echo 'Severity: ' . \$v->severity . PHP_EOL;
        echo 'Description: ' . substr(\$v->description, 0, 100) . '...' . PHP_EOL;
        echo 'CVSS: ' . (\$v->cvss_score ?? 'N/A') . PHP_EOL;
        echo 'CVE: ' . (\$v->cve ?? 'N/A') . PHP_EOL;
    }}
}}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        # 3. Проверяем API endpoint
        print("\n3. Проверка API endpoint:")
        cmd = f'''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$pentest = App\\\\Models\\\\Pentest::find('{pentest_id}');
if (\$pentest) {{
    \$action = new App\\\\Domain\\\\Vulnerabilities\\\\Actions\\\\GetVulnerabilitiesByPentestAction();
    \$vulns = \$action->execute(\$pentest->id);
    echo 'API возвращает: ' . \$vulns->count() . ' уязвимостей' . PHP_EOL;
    foreach (\$vulns->take(3) as \$v) {{
        echo PHP_EOL . 'Title: ' . \$v->title . PHP_EOL;
        echo 'Severity: ' . \$v->severity . PHP_EOL;
        echo 'Data: ' . json_encode(\$v->toArray(), JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . PHP_EOL;
    }}
}}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        # 4. Проверяем папку с результатами
        print("\n4. Проверка папки с результатами:")
        report_dir = f"/root/shannon/pentest_reports/{pentest_id}"
        output, _, code = conn.execute(f"test -d {report_dir} && echo 'exists' || echo 'not found'")
        if 'exists' in output:
            print(f"   ✅ Папка найдена: {report_dir}")
            output, _, _ = conn.execute(f"ls -lh {report_dir}/")
            print(output)
        else:
            print(f"   ⚠️  Папка не найдена: {report_dir}")
        
        # 5. Создаем архив
        print("\n5. Создание архива результатов...")
        archive_name = f"pentest_{pentest_id}.tar.gz"
        archive_path = f"/tmp/{archive_name}"
        conn.execute(f"cd /root/shannon/pentest_reports && tar -czf {archive_path} {pentest_id}/ 2>&1")
        
        # Проверяем размер архива
        output, _, _ = conn.execute(f"ls -lh {archive_path}")
        print(f"   Архив создан: {archive_path}")
        print(output)
        
        # 6. Копируем архив локально через base64
        print("\n6. Копирование архива на локальную машину...")
        local_dir = "pentest_results"
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, archive_name)
        
        # Читаем архив через base64
        output, _, _ = conn.execute(f"base64 {archive_path}")
        archive_data = base64.b64decode(output)
        
        with open(local_path, 'wb') as f:
            f.write(archive_data)
        
        print(f"   ✅ Архив скопирован: {local_path}")
        
        # 7. Распаковываем локально
        print("\n7. Распаковка архива...")
        import tarfile
        extract_dir = os.path.join(local_dir, pentest_id)
        os.makedirs(extract_dir, exist_ok=True)
        
        with tarfile.open(local_path, 'r:gz') as tar:
            tar.extractall(extract_dir)
        
        print(f"   ✅ Результаты распакованы в: {extract_dir}")
        
        # Показываем содержимое
        print("\n8. Содержимое папки:")
        for root, dirs, files in os.walk(extract_dir):
            level = root.replace(extract_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                print(f'{subindent}{file} ({size} bytes)')
        
        print("\n" + "="*60)
        print("✅ РЕЗУЛЬТАТЫ СКОПИРОВАНЫ")
        print("="*60)
        print(f"\n📁 Локальная папка: {os.path.abspath(extract_dir)}")
        print(f"📦 Архив: {os.path.abspath(local_path)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_and_copy()

