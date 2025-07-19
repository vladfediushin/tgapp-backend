# 🚀 Deployment Guide - FSRS-only Version

## 📋 Prerequisites

- GitHub аккаунт
- Vercel аккаунт (для frontend)
- Render аккаунт (для backend + database)

## 🗄️ Backend Deployment (Render)

### 1. Создание PostgreSQL Database

1. Зайдите на [render.com](https://render.com)
2. Create New → PostgreSQL
3. Настройки:
   - **Name**: `tgapp-fsrs-db`
   - **Database**: `tgapp_fsrs`
   - **User**: `admin` (или любое имя)
   - **Region**: выберите ближайший
   - **Plan**: Free (для тестирования)

4. После создания сохраните:
   - **External Database URL** (для локальной разработки)
   - **Internal Database URL** (будет автоматически использоваться)

### 2. Создание Web Service

1. Create New → Web Service
2. Connect GitHub репозиторий: `tgapp-backend`
3. Настройки:
   - **Name**: `tgapp-fsrs-backend`
   - **Branch**: `feature/fsrs-only-migration`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. Environment Variables:
   ```
   DATABASE_URL = [Auto-fill from PostgreSQL service]
   PYTHON_VERSION = 3.11.0
   ```

5. Deploy!

### 3. Запуск миграций

После деплоя backend:

1. В Render Dashboard → Backend Service → Shell
2. Выполните команды:
   ```bash
   cd backend
   alembic upgrade head
   ```

## 🌐 Frontend Deployment (Vercel)

### 1. Подготовка конфигурации

Обновите API URL в frontend:

```typescript
// frontend/src/api/api.ts
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://tgapp-fsrs-backend.onrender.com'
  : 'http://localhost:8000';
```

### 2. Деплой на Vercel

1. Зайдите на [vercel.com](https://vercel.com)
2. New Project → Import Git Repository
3. Выберите репозиторий: `tgapp-backend`
4. Настройки:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. Environment Variables:
   ```
   VITE_API_URL = https://tgapp-fsrs-backend.onrender.com
   ```

6. Deploy!

## 🔧 Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

### Frontend (.env)
```bash
VITE_API_URL=https://your-backend.onrender.com
```

## ✅ Post-Deployment Checklist

1. **Backend Health Check**: `GET /health`
2. **Database Connection**: Проверьте логи в Render
3. **CORS**: Убедитесь что frontend может делать запросы
4. **FSRS Endpoints**: Тест API endpoints
5. **Database Migrations**: Проверьте что все таблицы созданы

## 🎯 FSRS API Endpoints

После деплоя доступны:

- `POST /fsrs/submit-answer` - Отправка ответа
- `POST /fsrs/submit-batch` - Массовая отправка
- `GET /fsrs/due-questions/{user_id}` - Вопросы к повторению
- `GET /fsrs/stats/{user_id}` - Статистика FSRS
- `GET /fsrs/card-info/{user_id}/{question_id}` - Инфо карточки

## 🐛 Troubleshooting

### Backend не стартует
- Проверьте логи в Render Dashboard
- Убедитесь что DATABASE_URL корректный
- Проверьте что все dependencies установлены

### Frontend не может подключиться к API
- Проверьте CORS настройки в backend/app/main.py
- Убедитесь что VITE_API_URL правильный
- Проверьте что backend доступен

### Database ошибки
- Убедитесь что миграции выполнены: `alembic upgrade head`
- Проверьте DATABASE_URL
- Проверьте что PostgreSQL сервис запущен

## 🎊 Success!

После успешного деплоя у вас будет:

- ✅ FSRS-only backend на Render
- ✅ React frontend на Vercel  
- ✅ PostgreSQL database
- ✅ Готовая система интервального повторения

**Enjoy your scientifically optimized spaced repetition system! 🧠✨**
