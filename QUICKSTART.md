# Быстрый запуск Shannon Pentest Platform

## Шаг 1: Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Создайте .env файл (скопируйте из .env.example и заполните)
# Обязательно заполните:
# - SECRET_KEY (любая случайная строка)
# - ANTHROPIC_API_KEY (ваш ключ Claude API)
# - SSH_HOST, SSH_USER, SSH_PASSWORD

python run.py
```

Backend запустится на http://localhost:8000

## Шаг 2: Frontend

```bash
cd template
npm install
npm run dev
```

Frontend запустится на http://localhost:5173

## Шаг 3: Вход

1. Откройте http://localhost:5173
2. Войдите:
   - Username: `admin`
   - Password: `513277`

## Шаг 4: Тест

1. Перейдите в "Сервисы"
2. Создайте новый сервис (например, https://example.com)
3. Перейдите в "Пентесты"
4. Создайте пентест для этого сервиса
5. Запустите пентест

## Важно

- Убедитесь что сервер 72.56.79.153 доступен
- Убедитесь что Claude API ключ правильный
- При первом запуске пентеста инструменты будут установлены автоматически (это может занять время)

## Проблемы?

Смотрите SETUP.md для подробной инструкции и решения проблем.

