# Архитектура Shannon Backend (Laravel)

## Принципы проектирования

Проект следует принципам из книги **Laravel Beyond CRUD**:

1. **Domain-Driven Design** - бизнес-логика в доменных слоях
2. **Action Classes** - каждое действие в отдельном классе
3. **Data Transfer Objects** - использование DTO для передачи данных
4. **Thin Controllers** - контроллеры только делегируют вызовы
5. **Query Objects** - сложные запросы вынесены в отдельные классы

## Структура проекта

```
app/
├── Domain/                    # Доменная логика
│   ├── Auth/
│   │   └── Actions/           # Действия аутентификации
│   ├── Services/
│   │   └── Actions/           # Действия для сервисов
│   ├── Pentests/
│   │   ├── Actions/           # Действия для пентестов
│   │   └── Engine/           # Pentest Engine
│   ├── Vulnerabilities/
│   │   └── Actions/          # Действия для уязвимостей
│   └── Logs/
│       └── Actions/          # Действия для логов
│
├── Data/                     # Data Transfer Objects
│   ├── Auth/
│   ├── Services/
│   ├── Pentests/
│   ├── Vulnerabilities/
│   └── Logs/
│
├── Http/
│   ├── Controllers/          # Тонкие контроллеры
│   │   └── Api/
│   ├── Requests/             # Form Requests (валидация)
│   └── Resources/            # API Resources
│
├── Models/                   # Eloquent модели
│   ├── User.php
│   ├── Service.php
│   ├── Pentest.php
│   ├── Vulnerability.php
│   └── Log.php
│
├── Services/                 # Внешние сервисы
│   ├── SshClientService.php
│   └── ClaudeApiService.php
│
└── Events/                   # События для Broadcasting
    └── PentestStatusUpdated.php
```

## Поток данных

### Создание пентеста

```
HTTP Request
    ↓
Controller::store()
    ↓
CreatePentestData::from()  (DTO)
    ↓
CreatePentestAction::execute()
    ↓
Model::create()
    ↓
PentestData::from()  (DTO)
    ↓
HTTP Response
```

### Запуск пентеста

```
HTTP Request
    ↓
Controller::start()
    ↓
StartPentestAction::execute()
    ↓
Model::update(status = 'running')
    ↓
dispatch() → Queue
    ↓
PentestEngine::run()
    ↓
SSH Commands → Tools
    ↓
ClaudeApiService → Analysis
    ↓
Model::vulnerabilities()->create()
    ↓
Event::broadcast() → WebSocket
```

## Domain Actions

### Принципы

1. **Один Action = одно действие**
2. **Action принимает DTO, возвращает DTO**
3. **Action не знает о HTTP**
4. **Action содержит бизнес-логику**

### Примеры

```php
// Создание сервиса
CreateServiceAction::execute(CreateServiceData $data): ServiceData

// Запуск пентеста
StartPentestAction::execute(string $id): void

// Получение уязвимостей
GetVulnerabilitiesByPentestAction::execute(string $pentestId): Collection<VulnerabilityData>
```

## Data Transfer Objects

### Использование spatie/laravel-data

```php
class PentestData extends Data
{
    public function __construct(
        public string $id,
        public string $name,
        public string $target_url,
        // ...
    ) {}
}

// Использование
$data = PentestData::from($model);
$data = PentestData::from($request->all());
return response()->json($data->toArray());
```

### Преимущества

1. **Типобезопасность** - строгая типизация данных
2. **Валидация** - автоматическая валидация при создании
3. **Сериализация** - легко преобразовать в JSON/Array
4. **Неизменяемость** - данные не могут быть изменены после создания

## Pentest Engine

### Архитектура

```
PentestEngine
    ├── checkSelfScanning()      # Проверка на self-scanning
    ├── run()                    # Главный метод выполнения
    ├── setStep()                # Обновление шага
    ├── runStep()                # Выполнение конкретного шага
    │   ├── runNmapScan()
    │   ├── runNiktoScan()
    │   ├── runNucleiScan()
    │   ├── runDirbScan()
    │   └── runSqlmapScan()
    ├── analyzeResults()         # Анализ через Claude API
    └── broadcastStatus()        # Отправка статуса через WebSocket
```

### Workflow Steps

1. **nmap** - Сканирование портов
2. **nikto** - Сканирование веб-сервера
3. **nuclei** - Сканирование уязвимостей
4. **dirb** - Перебор директорий
5. **sqlmap** - Проверка SQL инъекций

## Сервисы

### SshClientService

Выполнение команд через SSH или локально:

```php
$sshClient->execute('nmap -sV target.com');
```

### ClaudeApiService

Анализ результатов сканирования через Claude API:

```php
$analysis = $claudeApi->analyzeScanResults($tool, $results, $targetUrl);
```

## WebSocket / Broadcasting

### События

```php
broadcast(new PentestStatusUpdated($pentest, $status));
```

### Каналы

- `pentests` - обновления статуса пентестов

### События

- `status.updated` - обновление статуса пентеста

## База данных

### Модели

- **User** - пользователи системы
- **Service** - сервисы для тестирования
- **Pentest** - пентесты
- **Vulnerability** - найденные уязвимости
- **Log** - логи выполнения

### Связи

```
Pentest
    ├── hasMany(Vulnerability)
    └── hasMany(Log)
```

## Безопасность

1. **Sanctum** - аутентификация через токены
2. **Self-scanning check** - защита от сканирования самого себя
3. **Input validation** - валидация через Form Requests и DTO
4. **SQL injection** - защита через Eloquent ORM

## Тестирование

### Unit Tests

Тестирование Actions изолированно:

```php
public function test_create_service_action()
{
    $action = new CreateServiceAction();
    $data = CreateServiceData::from(['name' => 'Test', 'url' => 'https://test.com']);
    $result = $action->execute($data);
    
    $this->assertInstanceOf(ServiceData::class, $result);
}
```

### Feature Tests

Тестирование API endpoints:

```php
public function test_create_pentest()
{
    $response = $this->postJson('/api/pentests', [
        'name' => 'Test Pentest',
        'config' => ['targetUrl' => 'https://test.com']
    ]);
    
    $response->assertStatus(201);
}
```

## Производительность

1. **Queues** - асинхронное выполнение пентестов
2. **Eager Loading** - загрузка связанных данных
3. **Caching** - кэширование часто используемых данных
4. **Database Indexes** - индексы на часто запрашиваемых полях

## Масштабирование

1. **Horizon** - управление очередями
2. **Redis** - кэширование и очереди
3. **Load Balancing** - балансировка нагрузки
4. **Database Replication** - репликация БД

