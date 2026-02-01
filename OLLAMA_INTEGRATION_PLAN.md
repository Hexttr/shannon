# План интеграции Ollama для параллельной работы с Claude API

## 📋 Обзор

Реализация параллельной поддержки Claude API и Ollama для анализа результатов пентестов. Пользователь выбирает модель при создании пентеста.

---

## 🏗️ Архитектура

### 1. Структура сервисов

```
App\Services\
├── Contracts\
│   └── AiAnalysisServiceInterface.php    # Интерфейс для всех AI провайдеров
├── ClaudeApiService.php                   # Существующий сервис (рефакторинг)
├── OllamaApiService.php                  # Новый сервис для Ollama
└── AiServiceFactory.php                   # Фабрика для выбора провайдера
```

### 2. Интерфейс AI сервиса

```php
interface AiAnalysisServiceInterface
{
    public function analyzeScanResults(
        string $tool, 
        string $results, 
        string $targetUrl
    ): array;
}
```

### 3. Модификация PentestEngine

- Заменить прямую зависимость от `ClaudeApiService` на `AiAnalysisServiceInterface`
- Получать провайдер через фабрику на основе `$pentest->config['ai_provider']`

### 4. База данных

- Добавить поле `ai_provider` в `config` JSON (уже есть поле `config`)
- Значения: `'claude'` | `'ollama'`
- По умолчанию: `'claude'` (для обратной совместимости)

### 5. Frontend

- Добавить выбор модели в форму создания пентеста
- Radio buttons или Select: "Claude API" / "Ollama"
- Отправлять `config.aiProvider` в API

---

## 📝 План реализации

### Этап 1: Backend - Интерфейс и рефакторинг (30 мин)

1. **Создать интерфейс**
   - `backend-laravel/app/Services/Contracts/AiAnalysisServiceInterface.php`
   - Метод: `analyzeScanResults(string $tool, string $results, string $targetUrl): array`

2. **Рефакторинг ClaudeApiService**
   - Реализовать `AiAnalysisServiceInterface`
   - Переименовать метод не требуется (уже совпадает)

### Этап 2: Backend - Ollama сервис (45 мин)

3. **Создать OllamaApiService**
   - `backend-laravel/app/Services/OllamaApiService.php`
   - Реализовать `AiAnalysisServiceInterface`
   - Использовать Ollama API: `http://localhost:11434/api/generate` или `/api/chat`
   - Формат запроса: OpenAI-совместимый
   - Парсинг ответа аналогичен ClaudeApiService

4. **Конфигурация Ollama**
   - Добавить в `config/services.php`:
     ```php
     'ollama' => [
         'api_url' => env('OLLAMA_API_URL', 'http://localhost:11434/api'),
         'model' => env('OLLAMA_MODEL', 'llama3.2'), // или mistral, neural-chat
     ],
     ```

### Этап 3: Backend - Фабрика провайдеров (20 мин)

5. **Создать AiServiceFactory**
   - `backend-laravel/app/Services/AiServiceFactory.php`
   - Метод: `create(string $provider): AiAnalysisServiceInterface`
   - Поддерживать: `'claude'`, `'ollama'`
   - Fallback на Claude при неизвестном провайдере

6. **Регистрация в ServiceProvider**
   - `backend-laravel/app/Providers/AppServiceProvider.php`
   - Биндинг интерфейса через фабрику (опционально)

### Этап 4: Backend - Модификация PentestEngine (30 мин)

7. **Обновить PentestEngine**
   - Заменить `private ClaudeApiService $claudeApi` на `private AiServiceFactory $aiFactory`
   - В методе `analyzeResults()`:
     ```php
     $provider = $pentest->config['ai_provider'] ?? 'claude';
     $aiService = $this->aiFactory->create($provider);
     $analysis = $aiService->analyzeScanResults(...);
     ```

### Этап 5: Backend - Данные и валидация (20 мин)

8. **Обновить PentestConfigData**
   - Добавить поле `aiProvider?: string` (опционально, по умолчанию 'claude')

9. **Обновить CreatePentestRequest**
   - Добавить валидацию: `'config.aiProvider' => ['nullable', 'string', 'in:claude,ollama']`

10. **Обновить CreatePentestAction**
    - Сохранять `aiProvider` в `config` JSON

### Этап 6: Frontend - Форма выбора модели (45 мин)

11. **Обновить типы**
    - `template/src/types/index.ts`
    - Добавить `aiProvider?: 'claude' | 'ollama'` в `CreatePentestRequest.config`

12. **Обновить форму создания пентеста**
    - Найти компонент создания пентеста (вероятно в `Pentests.tsx`)
    - Добавить Radio buttons или Select для выбора модели
    - Значения: `'claude'`, `'ollama'`
    - По умолчанию: `'claude'`

### Этап 7: Установка Ollama на сервер (30 мин)

13. **Установить Ollama**
    - Скачать и установить Ollama на сервере
    - Запустить как systemd service
    - Загрузить модель (например, `llama3.2` или `mistral`)

14. **Проверка работы**
    - Тест API: `curl http://localhost:11434/api/tags`
    - Тест генерации через API

---

## 🔧 Технические детали

### Ollama API формат

**Endpoint:** `POST http://localhost:11434/api/generate` или `/api/chat`

**Запрос (generate):**
```json
{
  "model": "llama3.2",
  "prompt": "...",
  "stream": false
}
```

**Запрос (chat - рекомендуется):**
```json
{
  "model": "llama3.2",
  "messages": [
    {
      "role": "user",
      "content": "..."
    }
  ],
  "stream": false
}
```

**Ответ:**
```json
{
  "model": "llama3.2",
  "created_at": "...",
  "response": "...",
  "done": true
}
```

### Рекомендуемые модели Ollama

- **llama3.2** (3B) - быстрая, хорошее качество
- **mistral** (7B) - баланс скорости и качества
- **neural-chat** (7B) - специализированная на диалогах
- **llama3.1** (8B) - более мощная, но медленнее

---

## ✅ Чеклист реализации

- [ ] Этап 1: Интерфейс и рефакторинг ClaudeApiService
- [ ] Этап 2: Создание OllamaApiService
- [ ] Этап 3: Фабрика провайдеров
- [ ] Этап 4: Модификация PentestEngine
- [ ] Этап 5: Обновление данных и валидации
- [ ] Этап 6: Frontend форма выбора модели
- [ ] Этап 7: Установка Ollama на сервер
- [ ] Тестирование: создание пентеста с Claude
- [ ] Тестирование: создание пентеста с Ollama
- [ ] Тестирование: параллельная работа обоих провайдеров

---

## 🚀 Установка Ollama на сервер

### Шаги установки:

1. **Скачать Ollama:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Загрузить модель:**
   ```bash
   ollama pull llama3.2
   # или
   ollama pull mistral
   ```

3. **Проверить работу:**
   ```bash
   ollama list
   curl http://localhost:11434/api/tags
   ```

4. **Настроить systemd service (опционально):**
   ```ini
   [Unit]
   Description=Ollama Service
   After=network.target

   [Service]
   ExecStart=/usr/local/bin/ollama serve
   Restart=always
   User=root

   [Install]
   WantedBy=multi-user.target
   ```

5. **Добавить в .env:**
   ```env
   OLLAMA_API_URL=http://localhost:11434/api
   OLLAMA_MODEL=llama3.2
   ```

---

## 📊 Оценка времени

- **Backend разработка:** ~2.5 часа
- **Frontend разработка:** ~45 минут
- **Установка и настройка Ollama:** ~30 минут
- **Тестирование:** ~30 минут
- **Итого:** ~4 часа

---

## 🔍 Риски и решения

1. **Риск:** Ollama может быть медленнее Claude
   - **Решение:** Использовать более легкие модели (llama3.2 3B), добавить timeout

2. **Риск:** Разный формат ответов от Ollama
   - **Решение:** Унифицировать парсинг через общий метод `parseAnalysis()`

3. **Риск:** Ollama не запущен на сервере
   - **Решение:** Fallback на Claude при ошибке подключения к Ollama

4. **Риск:** Недостаточно памяти для модели
   - **Решение:** Использовать легкие модели (3B-7B), мониторить использование памяти

---

## 📝 Примечания

- Обратная совместимость: существующие пентесты без `ai_provider` будут использовать Claude
- Можно расширить в будущем: добавить другие провайдеры (OpenAI, Gemini)
- Мониторинг: логировать, какой провайдер использовался для каждого пентеста

