# Исправление ошибок анализа через Ollama

## Проблема

В логах постоянно появлялась ошибка:
```
Ошибка анализа результатов через ollama: SQLSTATE[23000]: Integrity constraint violation: 19 NOT NULL constraint failed: vulnerabilities.id
```

## Причина ошибки

1. **Отсутствие ID при создании уязвимостей**
   - Модель `Vulnerability` требует обязательное поле `id` (UUID)
   - При создании уязвимостей через `$pentest->vulnerabilities()->create()` не передавался `id`
   - SQLite выдавал ошибку NOT NULL constraint

2. **Проблемы с парсингом ответов Ollama**
   - Ollama иногда возвращает ответ в markdown code blocks: ` ```json {...} ``` `
   - Парсер не всегда корректно извлекал JSON из такого формата
   - Ollama иногда возвращает текстовый ответ вместо JSON

## Исправления

### 1. ✅ Добавлена генерация UUID для уязвимостей

**Файл:** `backend-laravel/app/Domain/Pentests/Engine/PentestEngine.php`

```php
foreach ($analysis['vulnerabilities'] ?? [] as $vuln) {
    $pentest->vulnerabilities()->create([
        'id' => Str::uuid()->toString(), // ← ДОБАВЛЕНО
        'title' => $vuln['title'] ?? 'Unknown',
        // ...
    ]);
}
```

### 2. ✅ Улучшен парсинг ответов Ollama

**Файл:** `backend-laravel/app/Services/OllamaApiService.php`

**Улучшения:**
- Более агрессивное удаление markdown code blocks
- Извлечение JSON из ответа даже если он обернут в текст
- Обработка случаев когда уязвимостей нет
- Улучшенные регулярные выражения для поиска JSON

```php
// Удаляем markdown code blocks если есть (более агрессивно)
$content = preg_replace('/```json\s*/i', '', $content);
$content = preg_replace('/```\s*/', '', $content);
// Удаляем все что до первой { и после последней }
if (preg_match('/\{.*\}/s', $content, $matches)) {
    $content = $matches[0];
}
```

### 3. ✅ Улучшен промпт для Ollama

**Изменения:**
- Более четкие инструкции о формате ответа
- Требование возвращать ТОЛЬКО JSON
- Обработка пустых результатов
- Запрет на использование markdown code blocks

## Результат

✅ **Ошибки исправлены:**
- Уязвимости теперь создаются с правильным UUID
- Парсинг Ollama обрабатывает markdown code blocks
- Улучшена обработка текстовых ответов

✅ **Изменения запушены в git:**
- Коммит: `f6cff60` - Improve Ollama JSON parsing for markdown code blocks
- Коммит: `869bb65` - Fix: Ollama integration - UUID for vulnerabilities, improved JSON parsing, CORS and login fixes

✅ **Применено на сервере:**
- Файлы обновлены
- Кэш очищен
- Queue worker перезапущен

## Текущее состояние

- ✅ Ollama работает и анализирует результаты
- ✅ Уязвимости создаются корректно
- ✅ Парсинг обрабатывает различные форматы ответов
- ✅ Ошибки больше не должны появляться

## Мониторинг

Для проверки что ошибки исправлены:
```bash
# Проверка логов Laravel
tail -f /root/shannon/backend-laravel/storage/logs/laravel.log | grep -i "ollama\|error"

# Проверка логов пентеста
# В интерфейсе проверьте что нет ошибок при анализе через Ollama
```

