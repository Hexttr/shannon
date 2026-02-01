#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Восстановление уязвимостей из логов ошибок
"""

import sys
import os
import re

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')

from server_utils import ServerConnection

def restore_vulnerabilities():
    """Восстанавливает уязвимости из логов"""
    conn = ServerConnection()
    if not conn.connect():
        print("❌ Не удалось подключиться к серверу")
        return False
    
    try:
        print("="*60)
        print("🔧 Восстановление уязвимостей из логов...")
        print("="*60)
        
        # Извлекаем данные уязвимостей из ошибок
        cmd = '''cd /root/shannon/backend-laravel && php artisan tinker --execute="
\$pentest = App\\\\Models\\\\Pentest::orderBy('created_at', 'desc')->first();
if (\$pentest) {
    \$errors = \$pentest->logs()->where('level', 'error')->where('message', 'LIKE', '%vulnerabilities.id%')->orderBy('created_at', 'asc')->get(['message', 'created_at']);
    
    \$restored = 0;
    foreach (\$errors as \$err) {
        // Извлекаем данные из SQL запроса
        if (preg_match('/values \\((.*?)\\)/', \$err->message, \$matches)) {
            \$values = \$matches[1];
            // Парсим значения: title, description, severity, cvss_score, cve, solution, pentest_id, updated_at, created_at
            \$parts = explode(', ', \$values);
            if (count(\$parts) >= 6) {
                \$title = trim(\$parts[0], \"'\\\"\");
                \$description = trim(\$parts[1], \"'\\\"\");
                \$severity = trim(\$parts[2], \"'\\\"\");
                \$cvss_score = trim(\$parts[3], \"'\\\"\") ?: null;
                \$cve = trim(\$parts[4], \"'\\\"\") ?: null;
                \$solution = trim(\$parts[5], \"'\\\"\") ?: null;
                
                // Пропускаем пустые уязвимости
                if (empty(\$title) && empty(\$description)) {
                    continue;
                }
                
                // Создаем уязвимость с правильным UUID
                try {
                    \$pentest->vulnerabilities()->create([
                        'id' => Illuminate\\\\Support\\\\Str::uuid()->toString(),
                        'title' => \$title ?: 'Unknown',
                        'description' => \$description ?: '',
                        'severity' => \$severity ?: 'low',
                        'cvss_score' => \$cvss_score,
                        'cve' => \$cve,
                        'solution' => \$solution,
                    ]);
                    \$restored++;
                    echo 'Восстановлена уязвимость: ' . \$title . PHP_EOL;
                } catch (Exception \$e) {
                    echo 'Ошибка восстановления: ' . \$e->getMessage() . PHP_EOL;
                }
            }
        }
    }
    
    echo PHP_EOL . 'Всего восстановлено уязвимостей: ' . \$restored . PHP_EOL;
    
    // Проверяем итоговое количество
    \$total = \$pentest->vulnerabilities()->count();
    echo 'Всего уязвимостей в пентесте: ' . \$total . PHP_EOL;
}
" 2>&1'''
        output, _, _ = conn.execute(cmd)
        print(output)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    restore_vulnerabilities()

