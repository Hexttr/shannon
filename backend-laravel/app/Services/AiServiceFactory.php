<?php

namespace App\Services;

use App\Services\Contracts\AiAnalysisServiceInterface;
use Illuminate\Support\Facades\Log;

class AiServiceFactory
{
    /**
     * Создает экземпляр AI сервиса на основе провайдера
     *
     * @param string $provider Название провайдера ('claude' или 'ollama')
     * @return AiAnalysisServiceInterface
     */
    public function create(string $provider): AiAnalysisServiceInterface
    {
        return match (strtolower($provider)) {
            'claude' => app(ClaudeApiService::class),
            'ollama' => app(OllamaApiService::class),
            default => $this->getDefaultProvider(),
        };
    }

    /**
     * Возвращает провайдер по умолчанию (Claude)
     * Используется для обратной совместимости
     */
    private function getDefaultProvider(): AiAnalysisServiceInterface
    {
        Log::warning('Неизвестный AI провайдер, используется Claude по умолчанию');
        return app(ClaudeApiService::class);
    }
}

