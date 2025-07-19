# TG App Driving - Optimized Version

Приложение для изучения теории вождения с современным React frontend и оптимизированным FastAPI backend.

## Backend Optimizations ✅

### Database Performance
- **NullPool**: Отключен connection pooling для serverless окружения (Vercel)
- **Prepared Statements**: Отключены для совместимости с Vercel Postgres
- **Query Optimization**: Исправлены N+1 проблемы в `get_daily_progress()`
- **Timeouts**: Оптимизированы для serverless среды (60s command timeout)

### Health Check
- `GET /health` - полная проверка API + database
- `GET /health/simple` - быстрая проверка API

### Session Management
- Отключен autoflush для оптимизации производительности
- Улучшена обработка ошибок в database sessions
- Добавлено логирование для отладки

### Code Quality
- Добавлены type hints
- Улучшена обработка исключений
- Оптимизированы SQL запросы с window functions

## Frontend Redesign ✅

### Modern UI Components
- **lucide-react**: Современные иконки вместо React Icons
- **BottomNavigation**: Единый футер на всех страницах (кроме Repeat)
- **LoadingSpinner**: Анимированный, responsive спиннер
- **CircularProgress**: Кастомный прогресс-бар

### Pages Redesigned
- **Home.tsx**: Карточки с плейсхолдерами, динамический streak, быстрые действия
- **Profile.tsx**: Современный дизайн, убрана кнопка настроек
- **ModeSelect.tsx**: Цветные карточки, inline-стили, улучшенный UX
- **Results.tsx**: Современная карточная структура, hover-эффекты
- **Statistics.tsx**: Новая страница со статистикой
- **Settings.tsx**: Обновленный дизайн настроек
- **Authorize.tsx**: Полностью переведен на inline-стили

### Features
- **Internationalization**: Поддержка русского/английского с правильным склонением
- **Dynamic Streak**: Подсчет streak с интернационализацией
- **Responsive Design**: Адаптивная верстка для всех устройств
- **Avatar Logic**: Гендерно-нейтральная иконка при отсутствии фото
- **Smart Exam Planning**: Автоматический расчет ежедневной цели на основе даты экзамена (80% времени на изучение, 20% на повторение)

## Tech Stack

### Frontend
- React 18
- TypeScript
- Vite
- i18next (интернационализация)
- lucide-react (иконки)

### Backend
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- asyncpg (драйвер)
- Alembic (миграции)

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
# Настройте DATABASE_URL в .env
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `GET /health` - Health check с проверкой БД
- `GET /health/simple` - Быстрый health check
- `GET /users/{user_id}/stats` - Статистика пользователя
- `GET /users/{user_id}/daily-progress` - Ежедневный прогресс
- `GET /questions` - Получение вопросов для тренировки
- `GET /questions/remaining-count` - Количество нерешенных вопросов для пользователя

## Deployment

Приложение оптимизировано для развертывания на:
- **Frontend**: Vercel/Netlify
- **Backend**: Vercel/Railway/Heroku
- **Database**: Vercel Postgres/Supabase

## Key Improvements

1. **Performance**: Устранены bottlenecks в database и N+1 проблемы
2. **Scalability**: NullPool для serverless, оптимизированные таймауты
3. **User Experience**: Современный UI, быстрые действия, плейсхолдеры
4. **Monitoring**: Health check endpoints для мониторинга
5. **Maintainability**: Type safety, лучшая структура кода

## Next Steps

- [ ] Добавить мониторинг (Sentry, Prometheus)
- [ ] Реализовать кэширование для статических данных
- [ ] Добавить тесты (pytest, Jest)
- [ ] CI/CD pipeline
- [ ] Database migration strategy
