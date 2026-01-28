# Shannon - Pentest Platform

Платформа для автоматизированного пентестинга с веб-интерфейсом и интеграцией Claude API.

## Структура проекта

```
shannon/
├── backend/          # FastAPI backend
├── frontend/         # React frontend (из template/)
├── template/         # Шаблон фронтенда
└── ARCHITECTURE.md   # Документация архитектуры
```

## Быстрый старт

### Backend

1. Перейдите в директорию backend:
```bash
cd backend
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `.env.example` и заполните переменные окружения

4. Запустите сервер:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен по адресу: http://localhost:8000
Документация: http://localhost:8000/docs

### Frontend

1. Перейдите в директорию frontend (или template):
```bash
cd template  # или cd frontend
```

2. Установите зависимости:
```bash
npm install
```

3. Запустите dev сервер:
```bash
npm run dev
```

## Учетные данные по умолчанию

- **Username:** admin
- **Password:** 513277

## Основные возможности

- ✅ Аутентификация с защитой от брутфорса
- ✅ Управление целевыми сервисами
- ✅ Создание и запуск пентестов
- ✅ Автоматическая установка инструментов пентестинга на сервере
- ✅ Выполнение полного сканирования (Nmap, Nikto, Nuclei, Dirb, SQLMap)
- ✅ Анализ результатов через Claude API
- ✅ Генерация отчетов (Markdown + PDF)
- ✅ Real-time обновления статуса (WebSocket - в разработке)

## Инструменты пентестинга

Платформа автоматически устанавливает следующие инструменты:
- Nmap - сканирование портов
- Nikto - сканирование веб-уязвимостей
- SQLMap - тестирование SQL инъекций
- Nuclei - автоматическое сканирование уязвимостей
- Dirb - поиск директорий
- Gobuster - поиск директорий
- WPScan - сканирование WordPress
- WhatWeb - идентификация веб-технологий
- Subfinder - поиск поддоменов
- HTTPx - HTTP прокси

## Архитектура

Подробная документация по архитектуре находится в файле [ARCHITECTURE.md](ARCHITECTURE.md)

## Лицензия

Проект создан для тестового стенда.

