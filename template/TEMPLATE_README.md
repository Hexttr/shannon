# Шаблон фронтенда

## Расположение
`C:\ubuntu\template`

## Содержимое

Шаблон содержит только UI компоненты и стили для последующей интеграции с функционалом Shannon.

### Структура:
```
template/
├── src/
│   ├── components/     # UI компоненты
│   │   ├── Layout.tsx
│   │   ├── Sidebar.tsx
│   │   ├── StatusBar.tsx
│   │   ├── Logo.tsx
│   │   ├── CVSSBadge.tsx
│   │   ├── VulnerabilitiesList.tsx
│   │   └── LoginModal.tsx
│   ├── pages/          # Страницы
│   │   ├── Home.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Pentests.tsx
│   │   ├── Reports.tsx
│   │   ├── Analytics.tsx
│   │   ├── Services.tsx
│   │   ├── About.tsx
│   │   └── Login.tsx
│   ├── App.tsx         # Главный компонент
│   ├── App.css         # Стили
│   ├── index.css       # Глобальные стили
│   └── main.tsx        # Точка входа
├── public/             # Статические файлы
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Что удалено/заменено:

- ❌ API логика (`services/api.ts`) - заменена на TODO комментарии
- ❌ Auth контекст (`contexts/AuthContext.tsx`) - заменен на TODO комментарии
- ❌ ProtectedRoute - заменен на TODO комментарии

## Что оставлено:

- ✅ Все UI компоненты
- ✅ Все страницы
- ✅ Стили (CSS, Tailwind)
- ✅ Конфигурация (Vite, TypeScript)
- ✅ Структура приложения

## Использование:

1. Скопируйте шаблон в новый проект
2. Добавьте API логику для интеграции с Shannon
3. Добавьте Auth контекст для аутентификации
4. Замените TODO комментарии на реальную функциональность

