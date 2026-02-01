<?php

require __DIR__ . '/backend-laravel/vendor/autoload.php';

$app = require_once __DIR__ . '/backend-laravel/bootstrap/app.php';
$app->make(\Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use App\Models\Pentest;
use Illuminate\Support\Str;

$pentest = Pentest::orderBy('created_at', 'desc')->first();

if (!$pentest) {
    echo "Пентест не найден\n";
    exit(1);
}

echo "Пентест: {$pentest->id}\n";
echo "URL: {$pentest->target_url}\n\n";

$errors = $pentest->logs()
    ->where('level', 'error')
    ->where('message', 'LIKE', '%vulnerabilities.id%')
    ->orderBy('created_at', 'asc')
    ->get(['message', 'created_at']);

echo "Найдено ошибок: " . $errors->count() . "\n\n";

$restored = 0;

foreach ($errors as $err) {
    // Извлекаем данные из SQL запроса
    if (preg_match('/values \((.*?)\)/', $err->message, $matches)) {
        $values = $matches[1];
        $parts = explode(', ', $values);
        
        if (count($parts) >= 6) {
            $title = trim($parts[0], "'\"");
            $description = trim($parts[1], "'\"");
            $severity = trim($parts[2], "'\"");
            $cvss_score = trim($parts[3], "'\"") ?: null;
            $cve = trim($parts[4], "'\"") ?: null;
            $solution = trim($parts[5], "'\"") ?: null;
            
            // Пропускаем пустые уязвимости
            if (empty($title) && empty($description)) {
                continue;
            }
            
            // Создаем уязвимость с правильным UUID
            try {
                $pentest->vulnerabilities()->create([
                    'id' => Str::uuid()->toString(),
                    'title' => $title ?: 'Unknown',
                    'description' => $description ?: '',
                    'severity' => $severity ?: 'low',
                    'cvss_score' => $cvss_score,
                    'cve' => $cve,
                    'solution' => $solution,
                ]);
                $restored++;
                echo "✅ Восстановлена: {$title}\n";
            } catch (\Exception $e) {
                echo "❌ Ошибка: {$e->getMessage()}\n";
            }
        }
    }
}

echo "\nВсего восстановлено: {$restored}\n";
$total = $pentest->vulnerabilities()->count();
echo "Всего уязвимостей в пентесте: {$total}\n";

