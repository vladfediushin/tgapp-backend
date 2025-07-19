import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession } from '../store/session'
import { getUserStats, UserStats, createUser, UserOut } from '../api/api'

// 🔧 Утилита для логгирования на Vercel
function logToVercel(message: string) {
  fetch('/api/logs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  }).catch(err => {
    console.error('[LOG ERROR]', err)
  })
}

const Home: React.FC = () => {
  const [userName, setUserName] = useState<string | null>(null)
  const [stats, setStats] = useState<UserStats | null>(null)
  const internalId = useSession(state => state.userId)
  const setInternalId = useSession(state => state.setUserId)
  const navigate = useNavigate()

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    const user = tg?.initDataUnsafe?.user

    logToVercel('[TG INIT] Telegram object: ' + (tg ? '✅ found' : '❌ not found'))
    logToVercel('[TG INIT] User object: ' + JSON.stringify(user))
    logToVercel('[TG INIT] VITE_API_BASE_URL: ' + import.meta.env.VITE_API_BASE_URL)

    if (tg && user) {
      tg.ready()
      tg.expand()
      setUserName(user.first_name || 'друг')

      // создаём через axios функцию createUser
      createUser({
        telegram_id: user.id,
        username: user.username,
        first_name: user.first_name,
        last_name: user.last_name,
      })
        .then(res => {
          const data: UserOut = res.data
          logToVercel(`[TG INIT] createUser response id=${data.id}`)
          // сохраняем внутренний UUID в сторадж
          setInternalId(data.id)
        })
        .catch(err => {
          logToVercel('[TG INIT] createUser error: ' + err.message)
        })
    } else {
      logToVercel('[TG INIT] Telegram WebApp or user not available')
    }
  }, [setInternalId])

  useEffect(() => {
    if (!internalId) return
    getUserStats(internalId)
      .then(res => setStats(res.data))
      .catch(err => console.error('Ошибка получения статистики', err))
  }, [internalId])

  const handleStart = () => {
    navigate('/mode')
  }

  const handleProfile = () => {
    navigate('/profile')
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>Привет, {userName}!</h2>

      {stats ? (
        <p>
          Пройдено: {stats.answered} из {stats.total_questions}, верных: {stats.correct}
        </p>
      ) : (
        <p>Загрузка статистики...</p>
      )}

      <button
        style={{
          display: 'block',
          width: '100%',
          padding: '12px',
          marginTop: '20px',
          fontSize: '16px',
          backgroundColor: '#2AABEE',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
        }}
        onClick={handleStart}
      >
        Начать повторение
      </button>

      <button
        style={{
          display: 'block',
          width: '100%',
          padding: '10px',
          marginTop: '10px',
          fontSize: '14px',
          backgroundColor: '#ECECEC',
          border: '1px solid #CCC',
          borderRadius: '8px',
        }}
        onClick={handleProfile}
      >
        Личный кабинет
      </button>
    </div>
  )
}

export default Home