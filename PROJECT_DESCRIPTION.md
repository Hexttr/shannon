# Shannon - Платформа для автоматизированного пентестинга

## Описание проекта

**Shannon** — веб-платформа для автоматизированного проведения пентестов (penetration testing) с возможностью управления сервисами, запуска сканирований, анализа уязвимостей и генерации отчетов.

### Основные возможности

- 🔐 **Аутентификация и авторизация** — защищенный доступ к системе
- 🎯 **Управление сервисами** — добавление и отслеживание целевых сервисов для тестирования
- 🛡️ **Автоматизированные пентесты** — запуск комплексных сканирований с использованием множества инструментов
- 📊 **Мониторинг в реальном времени** — отслеживание прогресса пентестов через WebSocket
- 🔍 **Анализ уязвимостей** — автоматический анализ результатов с помощью Claude API
- 📄 **Генерация отчетов** — создание PDF-отчетов по результатам пентестов
- 📈 **Аналитика** — визуализация статистики и метрик
- 🔄 **Workflow визуализация** — отслеживание этапов выполнения пентеста

---

## Архитектура

### Общая структура

```
shannon/
├── backend/          # Backend API сервер
│   └── app/
│       ├── api/      # REST API endpoints
│       ├── core/     # Бизнес-логика (pentest engine, SSH client, Claude client)
│       ├── models/   # SQLAlchemy модели БД
│       ├── schemas/  # Pydantic схемы для валидации
│       └── services/ # Сервисный слой
├── template/         # Frontend приложение
│   └── src/
│       ├── components/  # React компоненты
│       ├── pages/       # Страницы приложения
│       ├── services/    # API клиенты
│       ├── contexts/    # React контексты (Auth)
│       └── types/       # TypeScript типы
└── pentest_*_reports/  # Отчеты пентестов
```

### Архитектурный паттерн

**Backend:** RESTful API + WebSocket (Socket.IO)  
**Frontend:** SPA (Single Page Application) с React Router  
**Коммуникация:** HTTP/HTTPS + WebSocket для real-time обновлений

---

## Технологический стек

### Backend

| Технология | Версия/Описание | Назначение |
|------------|-----------------|------------|
| **Python** | 3.14 | Основной язык программирования |
| **FastAPI** | Latest | REST API фреймворк |
| **Uvicorn** | Latest | ASGI сервер для запуска FastAPI |
| **SQLAlchemy** | Latest | ORM для работы с БД |
| **SQLite** | Latest | База данных |
| **Socket.IO** | Latest | WebSocket для real-time коммуникации |
| **Pydantic** | Latest | Валидация данных и схемы |
| **Paramiko** | Latest | SSH клиент для удаленного выполнения команд |
| **Anthropic Claude API** | Latest | AI-анализ результатов сканирования |
| **python-socketio** | Latest | Socket.IO сервер для Python |

### Frontend

| Технология | Версия/Описание | Назначение |
|------------|-----------------|------------|
| **TypeScript** | 5.3.3 | Типизированный JavaScript |
| **React** | 18.2.0 | UI библиотека |
| **React Router** | 6.21.1 | Маршрутизация SPA |
| **Vite** | 5.0.8 | Сборщик и dev-сервер |
| **TanStack Query** | 5.17.0 | Управление состоянием сервера и кэширование |
| **Axios** | 1.6.2 | HTTP клиент |
| **Socket.IO Client** | 4.7.2 | WebSocket клиент |
| **TailwindCSS** | 3.4.0 | CSS фреймворк для стилизации |
| **Recharts** | 3.6.0 | Библиотека для графиков и диаграмм |
| **React Icons** | 5.5.0 | Иконки |

### Инструменты пентестинга

- **Nmap** — сканирование портов и сетевых сервисов
- **Nikto** — сканирование веб-серверов на известные уязвимости
- **Nuclei** — быстрый сканер уязвимостей на основе шаблонов
- **Dirb** — перебор директорий и файлов
- **SQLMap** — автоматическое обнаружение и эксплуатация SQL injection

### Инфраструктура

- **Nginx** — веб-сервер и reverse proxy
- **Systemd** — управление сервисами (автозапуск backend)
- **Let's Encrypt / Certbot** — SSL/TLS сертификаты
- **SSH** — удаленное выполнение команд на сервере

---

## Языки программирования

### Основные языки

1. **Python** (~70% кода)
   - Backend API
   - Бизнес-логика пентестинга
   - Интеграция с инструментами сканирования
   - Работа с БД

2. **TypeScript** (~25% кода)
   - Frontend приложение
   - Типизация API запросов
   - Компоненты React

3. **JavaScript** (~5% кода)
   - Конфигурационные файлы (Vite, Tailwind)
   - Утилиты сборки

### Дополнительные языки/форматы

- **SQL** — запросы к БД (SQLite)
- **CSS** — стили (TailwindCSS)
- **HTML** — шаблоны
- **Shell/Bash** — скрипты развертывания
- **Markdown** — документация

---

## Архитектура компонентов

### Backend компоненты

1. **API Layer** (`app/api/`)
   - `auth.py` — аутентификация и авторизация
   - `services.py` — управление сервисами
   - `pentests.py` — управление пентестами
   - `vulnerabilities.py` — управление уязвимостями
   - `logs.py` — логирование

2. **Core Engine** (`app/core/`)
   - `pentest_engine.py` — основной движок пентестинга
   - `ssh_client.py` — SSH клиент для выполнения команд
   - `claude_client.py` — интеграция с Claude API
   - `tools_installer.py` — установка инструментов сканирования

3. **Data Layer** (`app/models/`)
   - `user.py` — модель пользователя
   - `service.py` — модель сервиса
   - `pentest.py` — модель пентеста
   - `vulnerability.py` — модель уязвимости
   - `log.py` — модель лога

4. **Schemas** (`app/schemas/`)
   - Pydantic схемы для валидации запросов/ответов

### Frontend компоненты

1. **Pages** (`src/pages/`)
   - `Login.tsx` — страница входа
   - `Home.tsx` — главная страница (dashboard)
   - `Services.tsx` — управление сервисами
   - `Pentests.tsx` — управление пентестами
   - `Reports.tsx` — отчеты
   - `Analytics.tsx` — аналитика
   - `Workflow.tsx` — визуализация workflow

2. **Components** (`src/components/`)
   - `Layout.tsx` — основной layout с сайдбаром
   - `Sidebar.tsx` — боковое меню
   - `LogViewer.tsx` — просмотр логов
   - `StatusBar.tsx` — статус-бар
   - `VulnerabilitiesList.tsx` — список уязвимостей

3. **Services** (`src/services/`)
   - `authApi.ts` — API для аутентификации
   - `serviceApi.ts` — API для сервисов
   - `pentestApi.ts` — API для пентестов

4. **Contexts** (`src/contexts/`)
   - `AuthContext.tsx` — контекст аутентификации

---

## Поток данных

### Запуск пентеста

```
Frontend (React)
    ↓ HTTP POST /pentests
Backend API (FastAPI)
    ↓ Создание записи в БД
Pentest Engine (Python Thread)
    ↓ SSH команды
Инструменты сканирования (Nmap, Nikto, etc.)
    ↓ Результаты
Pentest Engine
    ↓ Claude API анализ
Анализ уязвимостей
    ↓ Сохранение в БД
WebSocket уведомление
    ↓ Real-time обновление
Frontend (React)
```

### Real-time обновления

```
Backend (Socket.IO Server)
    ↓ WebSocket события
Frontend (Socket.IO Client)
    ↓ React Query invalidation
UI обновление
```

---

## Безопасность

- ✅ Проверка на self-scanning (защита от white box тестирования самого себя)
- ✅ JWT токены для аутентификации
- ✅ HTTPS/SSL через Let's Encrypt
- ✅ Валидация входных данных через Pydantic
- ✅ Защищенные маршруты на frontend

---

## Развертывание

### Серверная инфраструктура

- **ОС:** Linux (Ubuntu/Debian)
- **Веб-сервер:** Nginx (reverse proxy)
- **Backend:** Systemd service (автозапуск)
- **База данных:** SQLite (файловая БД)
- **SSL:** Let's Encrypt сертификаты

### Порты

- **80/443** — Nginx (HTTP/HTTPS)
- **8000** — Backend API (FastAPI + Socket.IO)

---

## Особенности реализации

1. **Асинхронное выполнение пентестов** — каждый пентест запускается в отдельном потоке
2. **Workflow tracking** — отслеживание этапов выполнения (nmap → nikto → nuclei → dirb → sqlmap)
3. **Graceful error handling** — продолжение работы даже при ошибках API (Claude)
4. **Real-time мониторинг** — WebSocket для обновления статуса в реальном времени
5. **Автоматическая генерация отчетов** — PDF отчеты с результатами сканирования

---

## Версия

**v0.1.0** — Initial release

---

*Документ создан: 2026-01-29*


