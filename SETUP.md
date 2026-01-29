# Инструкция по запуску Shannon Pentest Platform

## Быстрый старт

### 1. Backend

```bash
cd backend

# Создайте виртуальное окружение
python -m venv venv
venv\Scripts\activate  # Windows
# или
source venv/bin/activate  # Linux/Mac

# Установите зависимости
pip install -r requirements.txt

# Создайте файл .env на основе .env.example
# Заполните переменные окружения (особенно SECRET_KEY, ANTHROPIC_API_KEY, SSH настройки)

# Запустите сервер
python run.py
# или
uvicorn app.main:socketio_app --reload --host 0.0.0.0 --port 8000
```

Backend будет доступен по адресу: http://localhost:8000
API документация: http://localhost:8000/docs

### 2. Frontend

```bash
cd template  # или cd frontend если скопировали

# Установите зависимости
npm install

# Создайте файл .env на основе .env.example (опционально)
# По умолчанию используется http://localhost:8000

# Запустите dev сервер
npm run dev
```

Frontend будет доступен по адресу: http://localhost:5173

## Учетные данные

- **Username:** admin
- **Password:** 513277

## Проверка работы

1. Откройте http://localhost:5173
2. Войдите с учетными данными admin/513277
3. Создайте сервис (например, https://example.com)
4. Создайте пентест для этого сервиса
5. Запустите пентест

## Возможные проблемы

### Backend не запускается
- Проверьте что все зависимости установлены: `pip install -r requirements.txt`
- Проверьте что файл .env создан и заполнен
- Проверьте что порт 8000 свободен

### Frontend не подключается к API
- Проверьте что backend запущен на http://localhost:8000
- Проверьте CORS настройки в backend/app/config.py
- Проверьте переменную VITE_API_URL в .env файле фронтенда

### Ошибки подключения к SSH серверу
- Проверьте что сервер доступен: `ping 72.56.79.153`
- Проверьте SSH настройки в .env файле
- Проверьте что пароль правильный

### Ошибки Claude API
- Проверьте что ANTHROPIC_API_KEY правильный в .env
- Проверьте баланс API ключа

## Структура проекта

```
shannon/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Бизнес-логика
│   │   ├── models/   # Модели БД
│   │   └── schemas/  # Pydantic схемы
│   ├── run.py        # Скрипт запуска
│   └── requirements.txt
│
└── template/         # React frontend
    ├── src/
    │   ├── services/ # API клиенты
    │   ├── contexts/  # React контексты
    │   ├── pages/    # Страницы
    │   └── components/ # Компоненты
    └── package.json
```


