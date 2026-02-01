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
                        'num_predict' => 4096, // Максимальное количество токенов
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
                        'num_predict' => 4096,
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
        $maxResultsLength = 10000; // Ограничиваем до 10k символов
        if (mb_strlen($results) > $maxResultsLength) {
            $results = mb_substr($results, 0, $maxResultsLength) . "\n... (результат обрезан для анализа)";
        }

        return "Проанализируй результаты сканирования безопасности для {$targetUrl}.\n\n" .
            "Инструмент: {$tool}\n\n" .
            "Результаты:\n{$results}\n\n" .
            "Извлеки все найденные уязвимости и верни их в формате JSON:\n" .
            "{\n" .
            "  \"vulnerabilities\": [\n" .
            "    {\n" .
            "      \"title\": \"Название уязвимости\",\n" .
            "      \"description\": \"Описание\",\n" .
            "      \"severity\": \"critical|high|medium|low\",\n" .
            "      \"cvss_score\": \"X.X\",\n" .
            "      \"cve\": \"CVE-XXXX-XXXX\",\n" .
            "      \"solution\": \"Рекомендации по исправлению\"\n" .
            "    }\n" .
            "  ]\n" .
            "}\n\n" .
            "ВАЖНО: Верни ТОЛЬКО валидный JSON без дополнительного текста.";
    }

    private function parseAnalysis(string $content): array
    {
        // Извлекаем JSON из ответа (может быть обернут в markdown code blocks)
        $content = trim($content);
        
        // Удаляем markdown code blocks если есть
        $content = preg_replace('/```json\s*/', '', $content);
        $content = preg_replace('/```\s*/', '', $content);
        $content = trim($content);
        
        // Ищем JSON объект
        if (preg_match('/\{.*\}/s', $content, $matches)) {
            $json = json_decode($matches[0], true);
            if (json_last_error() === JSON_ERROR_NONE && isset($json['vulnerabilities'])) {
                return $json;
            }
        }

        // Если не удалось распарсить, пытаемся найти vulnerabilities напрямую
        Log::warning('Ollama: Не удалось распарсить JSON из ответа. Ответ: ' . substr($content, 0, 500));
        return ['vulnerabilities' => []];
    }
}

