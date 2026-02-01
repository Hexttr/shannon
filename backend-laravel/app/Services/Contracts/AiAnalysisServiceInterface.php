<?php

namespace App\Services\Contracts;

interface AiAnalysisServiceInterface
{
    /**
     * Анализирует результаты сканирования безопасности и извлекает уязвимости
     *
     * @param string $tool Название инструмента сканирования (nmap, nikto, nuclei, etc.)
     * @param string $results Результаты сканирования в текстовом формате
     * @param string $targetUrl URL целевого сервера
     * @return array Массив с ключом 'vulnerabilities', содержащий список найденных уязвимостей
     */
    public function analyzeScanResults(string $tool, string $results, string $targetUrl): array;
}

