<?php

namespace App\Services;

use App\Services\Contracts\AiAnalysisServiceInterface;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class OllamaApiService implements AiAnalysisServiceInterface
{
    private string $apiUrl;
    private string $model;

    public function __construct()
    {
        $this->apiUrl = config('services.ollama.api_url', 'http://localhost:11434/api');
        $this->model = config('services.ollama.model', 'llama3.2:3b');
    }

    public function analyzeScanResults(string $tool, string $results, string $targetUrl): array
    {
        try {
            $prompt = $this->buildPrompt($tool, $results, $targetUrl);

            // Используем /api/chat endpoint для лучшей совместимости
            $response = Http::timeout(300) // 5 минут timeout для больших результатов
                ->post("{$this->apiUrl}/chat", [
                    'model' => $this->model,
                    'messages' => [
                        [
                            'role' => 'user',
                            'content' => $prompt,
                        ],
                    ],
                    'stream' => false,
                    'options' => [
                        'temperature' => 0.3, // Низкая температура для более точного анализа
                        'num_predict' => 8192, // Увеличено до 8k токенов для более детального анализа
                    ],
                ]);

            if ($response->successful()) {
                $content = $response->json('message.content', '');
                
                if (empty($content)) {
                    // Fallback на /api/generate если /api/chat не поддерживается
                    $content = $this->tryGenerateEndpoint($prompt);
                }
                
                return $this->parseAnalysis($content);
            }

            Log::error('Ollama API error: ' . $response->body());
            return ['vulnerabilities' => []];
        } catch (\Exception $e) {
            Log::error('Ollama API exception: ' . $e->getMessage());
            return ['vulnerabilities' => []];
        }
    }

    /**
     * Fallback метод для использования /api/generate endpoint
     */
    private function tryGenerateEndpoint(string $prompt): string
    {
        try {
            $response = Http::timeout(300)
                ->post("{$this->apiUrl}/generate", [
                    'model' => $this->model,
                    'prompt' => $prompt,
                    'stream' => false,
                    'options' => [
                        'temperature' => 0.3,
                        'num_predict' => 8192, // Увеличено для более детального анализа
                    ],
                ]);

            if ($response->successful()) {
                return $response->json('response', '');
            }
        } catch (\Exception $e) {
            Log::warning('Ollama /api/generate fallback failed: ' . $e->getMessage());
        }

        return '';
    }

    private function buildPrompt(string $tool, string $results, string $targetUrl): string
    {
        // Обрезаем результаты если они слишком длинные (Ollama имеет ограничения)
        // Увеличено до 50k для более глубокого анализа (llama3.2:3b имеет ~8k токенов контекста)
        // Это примерно 20-30k символов, но оставляем запас для промпта
        $maxResultsLength = 50000; // Увеличено до 50k символов для более полного анализа
        if (mb_strlen($results) > $maxResultsLength) {
            // Обрезаем с конца, оставляя начало (там обычно важная информация)
            $results = mb_substr($results, 0, $maxResultsLength) . "\n... (результат обрезан для анализа, показаны первые " . number_format($maxResultsLength) . " символов)";
        }

        return "Ты - эксперт по кибербезопасности с глубокими знаниями об уязвимостях, CVE, CVSS и методах защиты.\n\n" .
            "Проанализируй результаты сканирования безопасности для {$targetUrl}.\n\n" .
            "Инструмент сканирования: {$tool}\n\n" .
            "Результаты сканирования:\n{$results}\n\n" .
            "ЗАДАЧА: Внимательно проанализируй результаты и извлеки ВСЕ найденные уязвимости безопасности.\n\n" .
            "Для каждой уязвимости определи:\n" .
            "- Название уязвимости (на основе паттернов в результатах)\n" .
            "- Описание (что именно обнаружено, почему это уязвимость)\n" .
            "- Уровень критичности (critical/high/medium/low на основе потенциального воздействия)\n" .
            "- CVSS score (если можешь оценить, иначе null)\n" .
            "- CVE номер (если упоминается в результатах, иначе пустая строка)\n" .
            "- Решение (конкретные рекомендации по исправлению)\n\n" .
            "Верни результат ТОЛЬКО в формате JSON (без дополнительного текста):\n" .
            "{\n" .
            "  \"vulnerabilities\": [\n" .
            "    {\n" .
            "      \"title\": \"Название уязвимости\",\n" .
            "      \"description\": \"Подробное описание на основе результатов сканирования\",\n" .
            "      \"severity\": \"critical|high|medium|low\",\n" .
            "      \"cvss_score\": \"X.X или null\",\n" .
            "      \"cve\": \"CVE-XXXX-XXXX или пустая строка\",\n" .
            "      \"solution\": \"Конкретные рекомендации по исправлению\"\n" .
            "    }\n" .
            "  ]\n" .
            "}\n\n" .
            "КРИТИЧЕСКИ ВАЖНО:\n" .
            "1. Верни ТОЛЬКО валидный JSON объект без markdown code blocks\n" .
            "2. Если уязвимостей не найдено, верни: {\"vulnerabilities\": []}\n" .
            "3. НЕ добавляй никакого текста до или после JSON\n" .
            "4. Анализируй результаты внимательно - даже небольшие признаки уязвимостей важны\n" .
            "5. Используй свои знания об уязвимостях для анализа паттернов в результатах";
    }

    private function parseAnalysis(string $content): array
    {
        // Извлекаем JSON из ответа (может быть обернут в markdown code blocks)
        $content = trim($content);
        
        // Проверяем если ответ говорит что уязвимостей нет
        $noVulnsPatterns = [
            '/ни.*уязвимост/i',
            '/no.*vulnerabilit/i',
            '/уязвимост.*не.*найден/i',
            '/vulnerabilit.*not.*found/i',
            '/не.*обнаружен/i',
            '/not.*detected/i',
        ];
        
        foreach ($noVulnsPatterns as $pattern) {
            if (preg_match($pattern, $content)) {
                Log::info('Ollama: Уязвимостей не обнаружено в ответе');
                return ['vulnerabilities' => []];
            }
        }
        
        // Удаляем markdown code blocks если есть (более агрессивно)
        $content = preg_replace('/```json\s*/i', '', $content);
        $content = preg_replace('/```\s*/', '', $content);
        // Удаляем все что до первой { и после последней }
        if (preg_match('/\{.*\}/s', $content, $matches)) {
            $content = $matches[0];
        }
        $content = trim($content);
        
        // Ищем JSON объект - пробуем несколько вариантов
        $jsonPatterns = [
            '/\{[^{}]*"vulnerabilities"[^{}]*\}/s', // Простой объект с vulnerabilities
            '/\{.*"vulnerabilities".*\}/s', // Полный объект
            '/\{.*\}/s', // Любой JSON объект
        ];
        
        foreach ($jsonPatterns as $pattern) {
            if (preg_match($pattern, $content, $matches)) {
                $json = json_decode($matches[0], true);
                if (json_last_error() === JSON_ERROR_NONE) {
                    // Проверяем структуру
                    if (isset($json['vulnerabilities']) && is_array($json['vulnerabilities'])) {
                        return $json;
                    }
                    // Если есть массив уязвимостей напрямую
                    if (isset($json[0]) && is_array($json[0]) && isset($json[0]['title'])) {
                        return ['vulnerabilities' => $json];
                    }
                }
            }
        }
        
        // Пытаемся найти JSON в многострочном ответе
        $lines = explode("\n", $content);
        foreach ($lines as $line) {
            $line = trim($line);
            if (strpos($line, '{') !== false && strpos($line, '}') !== false) {
                $json = json_decode($line, true);
                if (json_last_error() === JSON_ERROR_NONE && isset($json['vulnerabilities'])) {
                    return $json;
                }
            }
        }

        // Если не удалось распарсить, логируем и возвращаем пустой массив
        Log::warning('Ollama: Не удалось распарсить JSON из ответа. Ответ: ' . substr($content, 0, 500));
        return ['vulnerabilities' => []];
    }
}

