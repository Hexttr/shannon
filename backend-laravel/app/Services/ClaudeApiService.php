<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ClaudeApiService
{
    private string $apiKey;
    private string $apiUrl = 'https://api.anthropic.com/v1/messages';

    public function __construct()
    {
        $this->apiKey = config('services.claude.api_key');
    }

    public function analyzeScanResults(string $tool, string $results, string $targetUrl): array
    {
        if (!$this->apiKey) {
            Log::warning('Claude API key не настроен');
            return ['vulnerabilities' => []];
        }

        try {
            $prompt = $this->buildPrompt($tool, $results, $targetUrl);

            $response = Http::withHeaders([
                'x-api-key' => $this->apiKey,
                'anthropic-version' => '2023-06-01',
                'content-type' => 'application/json',
            ])->post($this->apiUrl, [
                'model' => 'claude-3-sonnet-20240229',
                'max_tokens' => 4096,
                'messages' => [
                    [
                        'role' => 'user',
                        'content' => $prompt,
                    ],
                ],
            ]);

            if ($response->successful()) {
                $content = $response->json('content.0.text', '');
                return $this->parseAnalysis($content);
            }

            Log::error('Claude API error: ' . $response->body());
            return ['vulnerabilities' => []];
        } catch (\Exception $e) {
            Log::error('Claude API exception: ' . $e->getMessage());
            return ['vulnerabilities' => []];
        }
    }

    private function buildPrompt(string $tool, string $results, string $targetUrl): string
    {
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
            "}";
    }

    private function parseAnalysis(string $content): array
    {
        // Извлекаем JSON из ответа
        if (preg_match('/\{.*\}/s', $content, $matches)) {
            $json = json_decode($matches[0], true);
            if (json_last_error() === JSON_ERROR_NONE) {
                return $json;
            }
        }

        return ['vulnerabilities' => []];
    }
}

