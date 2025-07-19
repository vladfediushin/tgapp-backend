// src/pages/Home.tsx
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession, loadUserWithCache } from '../store/session'
import { useStatsStore } from '../store/stats'
import {
  getAnswersByDay,
  UserStats
} from '../api/api'
import { useTranslation } from 'react-i18next'
import { calculateDailyGoal } from '../utils/dailyGoals'
import { getLast7LocalDates, calculateCurrentStreak } from '../utils/streakUtils'
import { getStreakText } from '../utils/pluralUtils'
import { loadStatsWithCache } from '../utils/statsSync'
import { Home as HomeIcon, User, BarChart3, Settings, Play, Flame, Calendar, ChevronRight, Sparkles, AlertCircle, Target } from 'lucide-react'
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar'
import 'react-circular-progressbar/dist/styles.css'
import i18n from 'i18next'
import BottomNavigation from '../components/BottomNavigation'

const Home = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  // Функция для получения правильного сообщения прогресса
  const getProgressMessage = (questionsToday: number, dailyGoal: number) => {
    if (questionsToday === 0) {
      return t('home.progressMessage.start') // 'Пора начать повторение'
    } else if (questionsToday > 0 && questionsToday < dailyGoal) {
      return t('home.progressMessage.keepGoing') // 'Молодец, поднажми!'
    } else {
      return t('home.progressMessage.excellent') // 'Отлично продвигаешься!'
    }
  }

  const [userName, setUserName] = useState(null)
  const [stats, setStats] = useState(null)
  const [userLoaded, setUserLoaded] = useState(false) // <- флаг загрузки user
  const [streakLoading, setStreakLoading] = useState(true)

  const internalId = useSession(state => state.userId)
  const cachedUser = useSession(state => state.cachedUser)
  const examCountry = useSession(state => state.examCountry)
  const examLanguage = useSession(state => state.examLanguage)
  const examDate = useSession(state => state.examDate)
  const manualDailyGoal = useSession(state => state.manualDailyGoal)
  const dailyProgress = useSession(state => state.dailyProgress)
  const dailyProgressDate = useSession(state => state.dailyProgressDate)
  const streakDays = useSession(state => state.streakDays)

  const setDailyProgress = useSession(state => state.setDailyProgress)
  const setExamCountry = useSession(state => state.setExamCountry)
  const setExamLanguage = useSession(state => state.setExamLanguage)
  const setUiLanguage = useSession(state => state.setUiLanguage)
  const setExamDate = useSession(state => state.setExamDate)
  const setManualDailyGoal = useSession(state => state.setManualDailyGoal)
  const setStreakDays = useSession(state => state.setStreakDays)

  // FSRS settings
  const useFSRS = useSession(state => state.useFSRS)
  const setUseFSRS = useSession(state => state.setUseFSRS)

  // Stats store hooks
  const isStatsLoading = useStatsStore(state => state.isStatsLoading)
  const isProgressLoading = useStatsStore(state => state.isProgressLoading)

  // Получаем имя пользователя и проверяем кэш
  useEffect(() => {
    const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user
    setUserName(tgUser?.first_name || 'друг')

    console.log('🏠 Home component mounting, telegramId:', tgUser?.id);
    console.log('🗂️ cachedUser in Home:', cachedUser ? `exists (id: ${cachedUser.id})` : 'null');

    // Если у нас есть кэш пользователя, используем его
    if (cachedUser) {
      console.log('🎯 Using cached user data in Home')
      
      // Обновляем только если значения изменились (чтобы не очищать кеш topics)
      if (cachedUser.exam_country && cachedUser.exam_country !== examCountry) {
        console.log(`🔄 Updating examCountry: ${examCountry} → ${cachedUser.exam_country}`)
        setExamCountry(cachedUser.exam_country)
      }
      if (cachedUser.exam_language && cachedUser.exam_language !== examLanguage) {
        console.log(`🔄 Updating examLanguage: ${examLanguage} → ${cachedUser.exam_language}`)
        setExamLanguage(cachedUser.exam_language)
      }
      
      if (cachedUser.ui_language) {
        setUiLanguage(cachedUser.ui_language)
        i18n.changeLanguage(cachedUser.ui_language)
      }
      if (cachedUser.exam_date) setExamDate(cachedUser.exam_date)
      if (cachedUser.daily_goal !== undefined && cachedUser.daily_goal !== null)
        setManualDailyGoal(cachedUser.daily_goal)

      setUserLoaded(true)
    } else if (tgUser?.id) {
      // Fallback: если нет кэша, загружаем данные с кешированием
      console.log('🔄 No cached user data, loading with cache in Home')
      loadUserWithCache(tgUser.id)
        .then(user => {
          // Обновляем только если значения изменились (чтобы не очищать кеш topics)
          if (user.exam_country && user.exam_country !== examCountry) {
            console.log(`🔄 Fallback: Updating examCountry: ${examCountry} → ${user.exam_country}`)
            setExamCountry(user.exam_country)
          }
          if (user.exam_language && user.exam_language !== examLanguage) {
            console.log(`🔄 Fallback: Updating examLanguage: ${examLanguage} → ${user.exam_language}`)
            setExamLanguage(user.exam_language)
          }
          
          if (user.ui_language) {
            setUiLanguage(user.ui_language)
            i18n.changeLanguage(user.ui_language)
          }
          if (user.exam_date) setExamDate(user.exam_date)
          if (user.daily_goal !== undefined && user.daily_goal !== null)
            setManualDailyGoal(user.daily_goal)

          setUserLoaded(true)
        })
        .catch(err => {
          console.error('Ошибка при получении пользователя:', err)
          setUserLoaded(true)
        })
    } else {
      setUserLoaded(true)
    }
  }, [cachedUser, examCountry, examLanguage])

  // Load stats and daily progress from cache or API
  useEffect(() => {
    if (!internalId || !userLoaded || !examCountry || !examLanguage) return

    loadStatsWithCache(internalId)
      .then(({ userStats, dailyProgress, fromCache }) => {
        setStats(userStats)
        setDailyProgress(dailyProgress.questions_mastered_today, dailyProgress.date)
        
        if (fromCache) {
          console.log('📦 Using cached stats data')
        } else {
          console.log('🔄 Loaded fresh stats data')
        }
      })
      .catch(err => {
        console.error('Error loading stats:', err)
      })
  }, [internalId, userLoaded, examCountry, examLanguage, setDailyProgress])

  // Загружаем streakDays только если их нет
  useEffect(() => {
    if (!internalId || !userLoaded) return
    if (streakDays && streakDays.length > 0) {
      setStreakLoading(false)
      return
    }
    getAnswersByDay(internalId, 7)
      .then(res => {
        setStreakDays(res.data)
        setStreakLoading(false)
      })
      .catch(err => {
        console.error('Ошибка загрузки streakDays:', err)
        setStreakDays([])
        setStreakLoading(false)
      })
  }, [internalId, userLoaded, streakDays, setStreakDays])

  const handleStart = () => {
    navigate('/mode')
  }

  const handleNewQuestions = () => {
    const params = new URLSearchParams({
      mode: 'new_only',
      batchSize: '30',
    })
    navigate(`/repeat?${params.toString()}`)
  }

  const handleIncorrectQuestions = () => {
    const params = new URLSearchParams({
      mode: 'incorrect',
      batchSize: '30',
    })
    navigate(`/repeat?${params.toString()}`)
  }

  const dailyGoalData = stats
    ? calculateDailyGoal(examDate, stats.total_questions, stats.correct)
    : null

  const finalDailyGoal = manualDailyGoal ?? dailyGoalData?.dailyGoal ?? null
  const todayQuestionsMastered = dailyProgress || 0
  const goalProgress = finalDailyGoal && finalDailyGoal > 0
    ? Math.min((todayQuestionsMastered / finalDailyGoal) * 100, 100)
    : 0

  // Вычисляем streak
  const streakProgress = streakDays.map(day => day.correct_answers)
  const currentStreak = finalDailyGoal && finalDailyGoal > 0
    ? calculateCurrentStreak(streakProgress, finalDailyGoal)
    : 0

  const today = new Date().toISOString().split('T')[0]
  const isProgressCurrent = dailyProgressDate === today

  const size = 150
  const strokeWidth = 12

  return (
    <>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
      <div style={{ 
        minHeight: '100vh', 
        backgroundColor: '#f8fafc', 
        paddingBottom: '80px' 
      }}>
        {/* Header */}
        <div style={{
          backgroundColor: 'white',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          padding: '16px 24px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div>
              <h1 style={{
                fontSize: '20px',
                fontWeight: 'bold',
                color: '#111827',
                margin: 0
              }}>
                {userName ? t('home.greeting', { name: userName }) : 'Привет, друг!'}
              </h1>
              <p style={{
                color: '#6b7280',
                margin: '4px 0 0 0',
                fontSize: '14px'
              }}>
                {userLoaded ? 'Продолжаем подготовку к экзамену' : 'Загружаем ваши данные...'}
              </p>
            </div>
            <div style={{ fontSize: '32px' }}>
              👨‍💼
            </div>
          </div>
        </div>

      <div style={{ padding: '24px', gap: '24px', display: 'flex', flexDirection: 'column' }}>
        {/* Progress Card - всегда показываем, но с плейсхолдерами */}
        <div style={{
          background: isProgressCurrent && finalDailyGoal !== null 
            ? 'linear-gradient(135deg, #059669 0%, #047857 100%)'
            : 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)',
          borderRadius: '16px',
          padding: '24px',
          color: 'white',
          opacity: (!userLoaded || (!examCountry || !examLanguage)) ? 0.7 : 1,
          transition: 'all 0.3s ease'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '16px'
          }}>
            <div>
              <h2 style={{
                fontSize: '18px',
                fontWeight: '600',
                margin: 0
              }}>
                {!userLoaded ? 'Загрузка...' : 
                 (!examCountry || !examLanguage) ? 'Настройте экзамен' :
                 isProgressCurrent && finalDailyGoal !== null ? t('home.todayProgress') : 'Дневная цель не установлена'}
              </h2>
              <p style={{
                color: 'rgba(255, 255, 255, 0.8)',
                margin: '4px 0 0 0',
                fontSize: '14px'
              }}>
                {!userLoaded ? 'Подготавливаем данные...' :
                 (!examCountry || !examLanguage) ? 'Перейдите в настройки' :
                 isProgressCurrent && finalDailyGoal !== null ? getProgressMessage(dailyProgress || 0, finalDailyGoal) : 'Установите дату экзамена'}
              </p>
            </div>
            <div style={{
              width: '80px',
              height: '80px',
              position: 'relative'
            }}>
              <svg width="80" height="80" style={{ transform: 'rotate(-90deg)' }}>
                <circle
                  cx="40"
                  cy="40"
                  r="30"
                  stroke="rgba(255, 255, 255, 0.3)"
                  strokeWidth="8"
                  fill="none"
                />
                <circle
                  cx="40"
                  cy="40"
                  r="30"
                  stroke="white"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={
                    !userLoaded || (!examCountry || !examLanguage) ? "0 188.5" :
                    isProgressCurrent && finalDailyGoal !== null ? `${(goalProgress / 100) * 188.5} 188.5` : "0 188.5"
                  }
                  strokeLinecap="round"
                  style={{ transition: 'stroke-dasharray 1s ease-out' }}
                />
              </svg>
              <div style={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <span style={{
                  fontSize: '13px',
                  fontWeight: 'bold',
                  color: 'white'
                }}>
                  {!userLoaded ? '...' :
                   (!examCountry || !examLanguage) ? '?' :
                   isProgressCurrent && finalDailyGoal !== null ? `${todayQuestionsMastered}/${finalDailyGoal}` : '0/0'}
                </span>
              </div>
            </div>
          </div>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px',
            marginTop: '16px'
          }}>
            <div style={{
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '8px',
              padding: '12px'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <Flame size={20} style={{ color: '#fb923c' }} />
                <span style={{ fontWeight: '600' }}>
                  {!userLoaded || streakLoading ? '...' : 
                   (!examCountry || !examLanguage || !finalDailyGoal) ? getStreakText(0, t) :
                   getStreakText(currentStreak, t)}
                </span>
              </div>
              <p style={{
                fontSize: '12px',
                color: 'rgba(255, 255, 255, 0.8)',
                margin: '4px 0 0 0'
              }}>
                Streak
              </p>
            </div>
            <div style={{
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '8px',
              padding: '12px',
              cursor: 'pointer'
            }}
            onClick={() => {
              navigate('/exam-settings')
            }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <Calendar size={20} style={{ color: '#60a5fa' }} />
                <span style={{ fontWeight: '600' }}>
                  {!userLoaded ? '...' :
                   examDate ? `${Math.ceil((new Date(examDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} дней` : 'Не установлено'}
                </span>
                <ChevronRight size={16} style={{ color: 'rgba(255, 255, 255, 0.8)', marginLeft: 'auto' }} />
              </div>
              <p style={{
                fontSize: '12px',
                color: 'rgba(255, 255, 255, 0.8)',
                margin: '4px 0 0 0'
              }}>
                До экзамена
              </p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div style={{ gap: '12px', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827',
            margin: 0
          }}>
            Быстрые действия
          </h3>
          
          <button 
            onClick={handleStart}
            style={{
              width: '100%',
              background: 'linear-gradient(135deg, #ea580c 0%, #dc2626 100%)',
              color: 'white',
              padding: '16px',
              borderRadius: '12px',
              border: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              fontSize: '16px'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-1px)'
              e.target.style.boxShadow = '0 4px 12px rgba(234, 88, 12, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)'
              e.target.style.boxShadow = 'none'
            }}
          >
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <Play size={24} />
              <span style={{ fontSize: '18px', fontWeight: '600' }}>
                {t('home.startRevision')}
              </span>
            </div>
            <ChevronRight size={20} />
          </button>

          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '12px'
          }}>
            <button 
              onClick={handleNewQuestions}
              style={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                padding: '16px',
                borderRadius: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = '#f9fafb'
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = 'white'
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '8px'
              }}>
                <Sparkles size={20} style={{ color: '#059669' }} />
                <span style={{ fontWeight: '500', color: '#111827' }}>Новые</span>
              </div>
              <p style={{
                fontSize: '12px',
                color: '#6b7280',
                margin: 0
              }}>
                Неизученные вопросы
              </p>
            </button>
            
            <button 
              onClick={handleIncorrectQuestions}
              style={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                padding: '16px',
                borderRadius: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = '#f9fafb'
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = 'white'
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '8px'
              }}>
                <AlertCircle size={20} style={{ color: '#dc2626' }} />
                <span style={{ fontWeight: '500', color: '#111827' }}>Ошибки</span>
              </div>
              <p style={{
                fontSize: '12px',
                color: '#6b7280',
                margin: 0
              }}>
                Работа над ошибками
              </p>
            </button>
          </div>
        </div>

        {/* FSRS Settings */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '16px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          marginBottom: '16px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '12px'
          }}>
            <h3 style={{
              fontSize: '16px',
              fontWeight: '600',
              color: '#111827',
              margin: 0,
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <Target size={18} style={{ color: '#3b82f6' }} />
              {t('fsrs.settings.enableFSRS')}
            </h3>
            <button
              onClick={() => setUseFSRS(!useFSRS)}
              style={{
                backgroundColor: useFSRS ? '#3b82f6' : '#e5e7eb',
                color: useFSRS ? 'white' : '#6b7280',
                border: 'none',
                borderRadius: '20px',
                padding: '6px 16px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              {useFSRS ? 'Включено' : 'Выключено'}
            </button>
          </div>
          <p style={{
            fontSize: '12px',
            color: '#6b7280',
            margin: 0
          }}>
            {t('fsrs.settings.description')}
          </p>
        </div>

        {/* Overall Progress - всегда показываем */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '16px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          opacity: (!userLoaded || !stats) ? 0.7 : 1,
          transition: 'all 0.3s ease'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '12px'
          }}>
            <h3 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#111827',
              margin: 0
            }}>
              Общий прогресс
            </h3>
            <span style={{
              fontSize: '14px',
              color: '#6b7280'
            }}>
              {!userLoaded || !stats ? '.../..' : `${stats.correct}/${stats.total_questions}`}
            </span>
          </div>
          
          <div style={{
            width: '100%',
            backgroundColor: '#e5e7eb',
            borderRadius: '9999px',
            height: '8px',
            marginBottom: '8px'
          }}>
            <div 
              style={{
                backgroundColor: '#059669',
                height: '8px',
                borderRadius: '9999px',
                transition: 'all 1s ease-out',
                width: (!userLoaded || !stats) ? '0%' : 
                       `${stats.total_questions > 0 ? Math.round((stats.correct / stats.total_questions) * 100) : 0}%`
              }}
            />
          </div>
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: 0
            }}>
              {(!userLoaded || !stats) ? 'Загрузка...' :
               `${stats.total_questions > 0 ? Math.round((stats.correct / stats.total_questions) * 100) : 0}% завершено`}
            </p>
            {(!userLoaded || !stats) && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid #e5e7eb',
                  borderTop: '2px solid #059669',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }} />
              </div>
            )}
          </div>
        </div>
        </div>

        {/* FSRS Statistics Section */}
        {stats?.fsrs_stats && (
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '16px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            marginTop: '16px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '12px'
            }}>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#111827',
                margin: 0,
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <BarChart3 size={20} style={{ color: '#3b82f6' }} />
                FSRS Analytics
              </h3>
            </div>
            
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: '12px'
            }}>
              <div style={{
                backgroundColor: '#f8fafc',
                borderRadius: '8px',
                padding: '12px',
                textAlign: 'center'
              }}>
                <div style={{
                  fontSize: '20px',
                  fontWeight: '600',
                  color: '#059669',
                  marginBottom: '4px'
                }}>
                  {Math.round(stats.fsrs_stats.retention_rate * 100)}%
                </div>
                <div style={{
                  fontSize: '12px',
                  color: '#6b7280'
                }}>
                  {t('fsrs.stats.retention')}
                </div>
              </div>
              
              <div style={{
                backgroundColor: '#f8fafc',
                borderRadius: '8px',
                padding: '12px',
                textAlign: 'center'
              }}>
                <div style={{
                  fontSize: '20px',
                  fontWeight: '600',
                  color: '#3b82f6',
                  marginBottom: '4px'
                }}>
                  {stats.fsrs_stats.avg_difficulty.toFixed(1)}
                </div>
                <div style={{
                  fontSize: '12px',
                  color: '#6b7280'
                }}>
                  {t('fsrs.stats.avgDifficulty')}
                </div>
              </div>
              
              <div style={{
                backgroundColor: '#f8fafc',
                borderRadius: '8px',
                padding: '12px',
                textAlign: 'center'
              }}>
                <div style={{
                  fontSize: '20px',
                  fontWeight: '600',
                  color: '#7c3aed',
                  marginBottom: '4px'
                }}>
                  {stats.fsrs_stats.total_reviews}
                </div>
                <div style={{
                  fontSize: '12px',
                  color: '#6b7280'
                }}>
                  {t('fsrs.stats.totalReviews')}
                </div>
              </div>
            </div>
          </div>
        )}

        <BottomNavigation />
      </div>
    </>
  )
}

export default Home
