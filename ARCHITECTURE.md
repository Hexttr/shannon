# Архитектура приложения Shannon - Pentest Platform

## Обзор

Shannon - это платформа для автоматизированного пентестинга с веб-интерфейсом, использующая Claude API для анализа результатов и генерации отчетов.

## Технологический стек

### Frontend
- **React 18** + **TypeScript**
- **Vite** - сборщик
- **Tailwind CSS** - стилизация
- **React Router** - маршрутизация
- **React Query (TanStack Query)** - управление состоянием и кэширование
- **Socket.io Client** - WebSocket для real-time обновлений
- **Recharts** - графики и визуализация

### Backend
- **Python 3.10+** - основной язык
- **FastAPI** - REST API фреймворк
- **SQLite/PostgreSQL** - база данных (SQLite для начала, PostgreSQL для production)
- **SQLAlchemy** - ORM
- **Pydantic** - валидация данных
- **Paramiko** - SSH подключения к серверу
- **Anthropic Claude API** - анализ результатов и генерация отчетов
- **Socket.io** - WebSocket сервер
- **Celery** (опционально) - асинхронные задачи
- **Pydantic Settings** - управление конфигурацией

### Инфраструктура
- **Сервер**: 72.56.79.153 (Ubuntu, SSH доступ)
- **Docker** (опционально) - контейнеризация

## Структура проекта

```
shannon/
├── frontend/                    # React приложение (из template/)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── contexts/
│   │   ├── services/            # API клиенты
│   │   └── types/               # TypeScript типы
│   └── package.json
│
├── backend/                     # Python FastAPI приложение
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Точка входа FastAPI
│   │   ├── config.py            # Конфигурация
│   │   ├── database.py          # Подключение к БД
│   │   │
│   │   ├── models/               # SQLAlchemy модели
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── service.py
│   │   │   ├── pentest.py
│   │   │   ├── vulnerability.py
│   │   │   └── log.py
│   │   │
│   │   ├── schemas/             # Pydantic схемы
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── service.py
│   │   │   ├── pentest.py
│   │   │   ├── vulnerability.py
│   │   │   └── auth.py
│   │   │
│   │   ├── api/                 # API роуты
│   │   │   ├── __init__.py
│   │   │   ├── deps.py          # Зависимости (auth, db)
│   │   │   ├── auth.py          # Аутентификация
│   │   │   ├── services.py      # CRUD сервисов
│   │   │   ├── pentests.py      # CRUD пентестов
│   │   │   ├── vulnerabilities.py
│   │   │   ├── logs.py
│   │   │   └── reports.py
│   │   │
│   │   ├── core/                # Бизнес-логика
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # JWT, хеширование паролей
│   │   │   ├── ssh_client.py    # SSH подключения через Paramiko
│   │   │   ├── pentest_engine.py # Движок пентестинга
│   │   │   ├── claude_client.py # Интеграция с Claude API
│   │   │   └── report_generator.py # Генерация отчетов
│   │   │
│   │   ├── services/            # Сервисный слой
│   │   │   ├── __init__.py
│   │   │   ├── pentest_service.py
│   │   │   ├── vulnerability_service.py
│   │   │   └── report_service.py
│   │   │
│   │   └── utils/               # Утилиты
│   │       ├── __init__.py
│   │       └── logger.py
│   │
│   ├── tests/                   # Тесты
│   ├── requirements.txt
│   └── .env.example
│
├── scripts/                     # Вспомогательные скрипты
│   ├── deploy.sh
│   └── setup_server.sh
│
├── docs/                        # Документация
│   └── API.md
│
├── docker-compose.yml           # Docker Compose конфигурация
├── .gitignore
└── README.md
```

## Архитектура компонентов

### 1. Frontend (React)

#### Компоненты
- **Layout** - основной layout с Sidebar
- **Sidebar** - навигационное меню
- **VulnerabilitiesList** - список уязвимостей
- **LogViewer** - просмотр логов пентеста
- **StatusBar** - статус выполнения
- **CVSSBadge** - бейдж CVSS оценки

#### Страницы
- **Home** - дашборд с метриками
- **Services** - управление целевыми сервисами
- **Pentests** - управление пентестами
- **Reports** - просмотр и генерация отчетов
- **Analytics** - аналитика и графики
- **Login** - аутентификация

#### API клиенты (services/)
- `api.ts` - базовый axios клиент
- `authApi.ts` - аутентификация
- `serviceApi.ts` - CRUD сервисов
- `pentestApi.ts` - CRUD пентестов
- `vulnerabilityApi.ts` - получение уязвимостей
- `reportApi.ts` - генерация отчетов

### 2. Backend (FastAPI)

#### Модели данных (models/)

**User**
- id, username, email, password_hash, created_at, updated_at

**Service**
- id, name, url, created_at, updated_at

**Pentest**
- id, name, service_id, target_url, status (pending/running/completed/failed/stopped)
- config (JSON), created_at, started_at, completed_at

**Vulnerability**
- id, pentest_id, type, title, severity (critical/high/medium/low)
- description, location, cvss_score, created_at

**Log**
- id, pentest_id, level (info/warning/error), message, timestamp

#### API Endpoints

**Auth**
- `POST /api/auth/login` - вход
- `POST /api/auth/logout` - выход
- `GET /api/auth/me` - текущий пользователь

**Services**
- `GET /api/services` - список сервисов
- `POST /api/services` - создать сервис
- `GET /api/services/{id}` - получить сервис
- `PUT /api/services/{id}` - обновить сервис
- `DELETE /api/services/{id}` - удалить сервис

**Pentests**
- `GET /api/pentests` - список пентестов
- `POST /api/pentests` - создать пентест
- `GET /api/pentests/{id}` - получить пентест
- `POST /api/pentests/{id}/start` - запустить пентест
- `POST /api/pentests/{id}/stop` - остановить пентест
- `DELETE /api/pentests/{id}` - удалить пентест
- `GET /api/pentests/{id}/status` - статус пентеста
- `GET /api/pentests/{id}/logs` - логи пентеста
- `GET /api/pentests/{id}/vulnerabilities` - уязвимости пентеста

**Reports**
- `POST /api/pentests/{id}/reports` - сгенерировать отчет
- `GET /api/pentests/{id}/reports/check` - проверить наличие отчета
- `GET /api/pentests/{id}/reports/pdf` - скачать PDF отчет

#### WebSocket Events

**Сервер → Клиент**
- `pentest:status` - обновление статуса пентеста
- `pentest:{id}:status` - статус конкретного пентеста
- `pentest:{id}:log` - новый лог пентеста
- `pentest:{id}:vulnerability` - новая уязвимость

### 3. Движок пентестинга (core/pentest_engine.py)

**Основные функции:**
1. **Подключение к серверу** через SSH (Paramiko)
2. **Выполнение инструментов пентестинга:**
   - Nmap - сканирование портов
   - Nikto - сканирование веб-уязвимостей
   - SQLMap - тестирование SQL инъекций
   - Dirb/Gobuster - поиск директорий
   - Nuclei - автоматическое сканирование уязвимостей
3. **Парсинг результатов** и извлечение уязвимостей
4. **Отправка результатов в Claude API** для анализа
5. **Сохранение результатов** в БД

**Процесс выполнения пентеста:**
```
1. Создание пентеста (status: pending)
2. Запуск пентеста (status: running)
3. Подключение к серверу через SSH
4. Выполнение инструментов пентестинга
5. Парсинг результатов
6. Отправка в Claude API для анализа
7. Сохранение уязвимостей в БД
8. Завершение пентеста (status: completed/failed)
```

### 4. Интеграция с Claude API (core/claude_client.py)

**Использование:**
- Анализ результатов сканирования
- Определение критичности уязвимостей
- Генерация описаний уязвимостей
- Генерация отчетов (Markdown + PDF)

**Промпты:**
- Анализ результатов Nmap/Nikto/SQLMap
- Классификация уязвимостей по CVSS
- Генерация рекомендаций по исправлению

### 5. Генерация отчетов (core/report_generator.py)

**Форматы:**
- **Markdown** - базовый формат
- **PDF** - для скачивания (через WeasyPrint или ReportLab)

**Содержание отчета:**
- Общая информация о пентесте
- Список найденных уязвимостей с описаниями
- Рекомендации по исправлению
- Графики и статистика

## Поток данных

### Создание и запуск пентеста

```
Frontend → POST /api/pentests
         → Backend создает запись в БД (status: pending)
         → Frontend → POST /api/pentests/{id}/start
         → Backend запускает асинхронную задачу
         → SSH подключение к серверу
         → Выполнение инструментов пентестинга
         → Парсинг результатов
         → Отправка в Claude API
         → Сохранение уязвимостей в БД
         → WebSocket: pentest:status
         → Frontend обновляет UI
```

### Real-time обновления

```
Backend → WebSocket: pentest:{id}:log
       → Frontend обновляет LogViewer

Backend → WebSocket: pentest:{id}:vulnerability
       → Frontend обновляет VulnerabilitiesList

Backend → WebSocket: pentest:status
       → Frontend обновляет список пентестов
```

## Безопасность

1. **Аутентификация**: JWT токены
2. **Хеширование паролей**: bcrypt
3. **CORS**: настройка для фронтенда
4. **Валидация входных данных**: Pydantic
5. **SQL Injection защита**: SQLAlchemy ORM
6. **SSH ключи**: использование SSH ключей вместо паролей (рекомендуется)

## Конфигурация

### Environment Variables (.env)

```env
# Database
DATABASE_URL=sqlite:///./shannon.db
# или для PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/shannon

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-...

# SSH Server
SSH_HOST=72.56.79.153
SSH_USER=root
SSH_PASSWORD=m8J@2_6whwza6U
SSH_PORT=22

# Server
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Logging
LOG_LEVEL=INFO
```

## Реализация (на основе ответов)

1. **Инструменты пентестинга:**
   - Все основные инструменты: Nmap, Nikto, SQLMap, Nuclei, Dirb, Gobuster, WPScan, etc.
   - Автоматическая установка инструментов на сервере при первом подключении

2. **Типы пентестов:**
   - Black box и White box пентесты
   - Всегда полный профиль сканирования

3. **Claude API:**
   - Полный анализ: классификация уязвимостей, генерация эксплойтов, рекомендации по исправлению

4. **Отчеты:**
   - Форматы: PDF, Markdown (остальное позже)

5. **Масштабирование:**
   - Один пользователь (admin)
   - Один пентест одновременно
   - Очередь задач не нужна

6. **Аутентификация:**
   - Один пользователь: admin/513277
   - Защита от брутфорса (rate limiting, блокировка после неудачных попыток)
   - Безопасное хранение пароля (bcrypt)

7. **Хранение данных:**
   - Хранение до удаления пользователем

## Следующие шаги

1. ✅ Проверка подключения к серверу
2. ⏳ Создание структуры проекта
3. ⏳ Настройка базы данных
4. ⏳ Реализация API endpoints
5. ⏳ Интеграция с SSH и инструментами пентестинга
6. ⏳ Интеграция с Claude API
7. ⏳ Реализация WebSocket для real-time обновлений
8. ⏳ Генерация отчетов
9. ⏳ Тестирование и деплой

