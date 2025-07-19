// Modern Profile.tsx with redesigned UI
import React, { useEffect, useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession, updateUserAndCache } from '../store/session'
import { useStatsStore } from '../store/stats'
import { useTranslation } from 'react-i18next'
import { loadStatsWithCache } from '../utils/statsSync'
import HomeButton from '../components/HomeButton'
import BottomNavigation from '../components/BottomNavigation'
import { User, Settings, Edit3, ChevronDown, Calendar, Target, TrendingUp, Activity, BarChart3 } from 'lucide-react'
import { calculateDailyGoal } from '../utils/dailyGoals'
import LoadingSpinner from '../components/LoadingSpinner'

const EXAM_COUNTRIES = [
  { value: 'am', label: '🇦🇲 Армения' },
  { value: 'kz', label: '🇰🇿 Казахстан' },
  { value: 'by', label: '🇧🇾 Беларусь' },
]

const EXAM_LANGUAGES = [
  { value: 'ru', label: 'Русский' },
  { value: 'en', label: 'English' },
]

const Profile = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  
  const userId = useSession(state => state.userId)
  const examCountry = useSession(state => state.examCountry)
  const examLanguage = useSession(state => state.examLanguage)
  const examDate = useSession(state => state.examDate)
  const manualDailyGoal = useSession(state => state.manualDailyGoal)

  const setExamCountry = useSession(state => state.setExamCountry)
  const setExamLanguage = useSession(state => state.setExamLanguage)

  // Stats store hooks
  const userStats = useStatsStore(state => state.userStats)
  const isStatsLoading = useStatsStore(state => state.isStatsLoading)

  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showCountrySelect, setShowCountrySelect] = useState(false)
  const [showLanguageSelect, setShowLanguageSelect] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!userId) {
      setLoading(false)
      return
    }

    // Try to load from cache first, then from API
    loadStatsWithCache(userId)
      .then(({ userStats, fromCache }) => {
        setStats(userStats)
        setError(null)
        if (fromCache) {
          console.log('📦 Using cached stats in Profile')
        } else {
          console.log('🔄 Loaded fresh stats in Profile')
        }
      })
      .catch(err => {
        console.error('Error loading profile stats:', err)
        setError('Failed to load profile data')
        setStats(null)
      })
      .finally(() => setLoading(false))
  }, [userId, examCountry, examLanguage])

  if (loading) {
    return <LoadingSpinner size={64} fullScreen />
  }

  if (error) {
    return (
      <div style={{
        minHeight: '100vh',
        backgroundColor: '#f8fafc',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px'
      }}>
        <div style={{ 
          color: '#dc2626', 
          marginBottom: '16px',
          fontSize: '18px',
          fontWeight: '600'
        }}>
          Ошибка: {error}
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button 
            onClick={() => window.location.reload()}
            style={{
              backgroundColor: '#059669',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '12px 24px',
              cursor: 'pointer'
            }}
          >
            Повторить
          </button>
          <button 
            onClick={() => navigate('/home')}
            style={{
              backgroundColor: '#6b7280',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '12px 24px',
              cursor: 'pointer'
            }}
          >
            На главную
          </button>
        </div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div style={{
        minHeight: '100vh',
        backgroundColor: '#f8fafc',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px'
      }}>
        <div style={{ 
          marginBottom: '16px',
          fontSize: '18px',
          fontWeight: '600'
        }}>
          Данные профиля недоступны
        </div>
        <button 
          onClick={() => navigate('/home')}
          style={{
            backgroundColor: '#059669',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            cursor: 'pointer'
          }}
        >
          На главную
        </button>
      </div>
    )
  }

  const { total_questions, answered, correct } = stats
  const incorrect = answered - correct
  const unanswered = total_questions - answered

  const dailyGoalData = stats
    ? calculateDailyGoal(examDate, stats.total_questions, stats.correct)
    : null
  const finalDailyGoal = manualDailyGoal ?? dailyGoalData?.dailyGoal ?? 10

  const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user
  const userName = tgUser?.first_name || 'User'
  const userPhotoUrl = tgUser?.photo_url

  // Функция для получения аватара
  const getUserAvatar = () => {
    if (userPhotoUrl) {
      return (
        <img 
          src={userPhotoUrl} 
          alt={userName}
          style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            objectFit: 'cover'
          }}
        />
      )
    }
    
    // Гендерно-нейтральная иконка пользователя
    return (
      <div style={{
        width: '64px',
        height: '64px',
        borderRadius: '50%',
        background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <User size={32} className="text-white" />
      </div>
    )
  }

  return (
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
          gap: '16px'
        }}>
          <HomeButton />
          <h1 style={{
            fontSize: '20px',
            fontWeight: 'bold',
            color: '#111827',
            margin: 0
          }}>
            {t('profile.title')}
          </h1>
        </div>
      </div>

      <div style={{ padding: '24px', gap: '24px', display: 'flex', flexDirection: 'column' }}>
        {/* User Profile Card */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '24px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            marginBottom: '20px'
          }}>
            {getUserAvatar()}
            <div style={{ flex: 1 }}>
              <h2 style={{
                fontSize: '24px',
                fontWeight: 'bold',
                color: '#111827',
                margin: '0 0 4px 0'
              }}>
                {userName}
              </h2>
              <p style={{
                color: '#6b7280',
                margin: 0,
                fontSize: '14px'
              }}>
                Изучающий теорию вождения
              </p>
            </div>
          </div>
          
          {/* Country and Language Selection */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '12px'
          }}>
            <button
              style={{
                backgroundColor: '#ecfdf5',
                border: '1px solid #d1fae5',
                borderRadius: '12px',
                padding: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                textAlign: 'left'
              }}
              onClick={() => setShowCountrySelect(true)}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <p style={{
                    fontSize: '12px',
                    color: '#059669',
                    fontWeight: '500',
                    margin: '0 0 4px 0'
                  }}>
                    Страна
                  </p>
                  <p style={{
                    fontSize: '14px',
                    color: '#111827',
                    margin: 0,
                    fontWeight: '500'
                  }}>
                    {EXAM_COUNTRIES.find(c => c.value === examCountry)?.label || 'Не выбрано'}
                  </p>
                </div>
                <ChevronDown size={16} color="#059669" />
              </div>
            </button>

            <button
              style={{
                backgroundColor: '#eff6ff',
                border: '1px solid #dbeafe',
                borderRadius: '12px',
                padding: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                textAlign: 'left'
              }}
              onClick={() => setShowLanguageSelect(true)}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <p style={{
                    fontSize: '12px',
                    color: '#2563eb',
                    fontWeight: '500',
                    margin: '0 0 4px 0'
                  }}>
                    Язык
                  </p>
                  <p style={{
                    fontSize: '14px',
                    color: '#111827',
                    margin: 0,
                    fontWeight: '500'
                  }}>
                    {EXAM_LANGUAGES.find(l => l.value === examLanguage)?.label || 'Не выбрано'}
                  </p>
                </div>
                <ChevronDown size={16} color="#2563eb" />
              </div>
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '16px'
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              backgroundColor: '#dcfce7',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 12px'
            }}>
              <Target size={24} color="#059669" />
            </div>
            <h3 style={{
              fontSize: '24px',
              fontWeight: 'bold',
              color: '#111827',
              margin: '0 0 4px 0'
            }}>
              {correct}
            </h3>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: 0
            }}>
              Правильных ответов
            </p>
          </div>

          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              backgroundColor: '#fef3c7',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 12px'
            }}>
              <BarChart3 size={24} color="#f59e0b" />
            </div>
            <h3 style={{
              fontSize: '24px',
              fontWeight: 'bold',
              color: '#111827',
              margin: '0 0 4px 0'
            }}>
              {total_questions > 0 ? Math.round((correct / total_questions) * 100) : 0}%
            </h3>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: 0
            }}>
              Общий прогресс
            </p>
          </div>
        </div>

        {/* Detailed Statistics */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827',
            margin: '0 0 16px 0'
          }}>
            Детальная статистика
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '8px 0',
              borderBottom: '1px solid #f3f4f6'
            }}>
              <span style={{ color: '#6b7280' }}>Всего вопросов</span>
              <span style={{ fontWeight: '600', color: '#111827' }}>{total_questions}</span>
            </div>
            
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '8px 0',
              borderBottom: '1px solid #f3f4f6'
            }}>
              <span style={{ color: '#6b7280' }}>Отвечено</span>
              <span style={{ fontWeight: '600', color: '#111827' }}>{answered}</span>
            </div>
            
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '8px 0',
              borderBottom: '1px solid #f3f4f6'
            }}>
              <span style={{ color: '#6b7280' }}>Правильно</span>
              <span style={{ fontWeight: '600', color: '#059669' }}>{correct}</span>
            </div>
            
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '8px 0',
              borderBottom: '1px solid #f3f4f6'
            }}>
              <span style={{ color: '#6b7280' }}>Неправильно</span>
              <span style={{ fontWeight: '600', color: '#dc2626' }}>{incorrect}</span>
            </div>
            
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '8px 0'
            }}>
              <span style={{ color: '#6b7280' }}>Не отвечено</span>
              <span style={{ fontWeight: '600', color: '#6b7280' }}>{unanswered}</span>
            </div>
          </div>
        </div>

        {/* Exam Date and Goal */}
        {examDate && (
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '16px'
            }}>
              <Calendar size={20} color="#059669" />
              <h3 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#111827',
                margin: 0
              }}>
                Экзамен
              </h3>
            </div>
            
            <div style={{
              backgroundColor: '#f8fafc',
              borderRadius: '8px',
              padding: '16px'
            }}>
              <p style={{
                fontSize: '16px',
                fontWeight: '600',
                color: '#111827',
                margin: '0 0 8px 0'
              }}>
                {new Date(examDate).toLocaleDateString('ru-RU', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </p>
              <p style={{
                fontSize: '14px',
                color: '#6b7280',
                margin: 0
              }}>
                Осталось дней: {Math.ceil((new Date(examDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))}
              </p>
            </div>
            
            {finalDailyGoal && (
              <div style={{
                marginTop: '16px',
                backgroundColor: '#eff6ff',
                borderRadius: '8px',
                padding: '16px'
              }}>
                <p style={{
                  fontSize: '14px',
                  color: '#2563eb',
                  margin: '0 0 4px 0',
                  fontWeight: '500'
                }}>
                  Ежедневная цель
                </p>
                <p style={{
                  fontSize: '18px',
                  fontWeight: '600',
                  color: '#111827',
                  margin: 0
                }}>
                  {finalDailyGoal} вопросов в день
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Country Selection Modal */}
      {showCountrySelect && (
        <div 
          style={{ 
            position: 'fixed', 
            top: 0, 
            left: 0, 
            width: '100vw', 
            height: '100vh', 
            background: 'rgba(0,0,0,0.5)', 
            zIndex: 1000, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            padding: '20px'
          }} 
          onClick={() => setShowCountrySelect(false)}
        >
          <div 
            style={{ 
              background: 'white', 
              borderRadius: '16px', 
              padding: '24px',
              width: '100%',
              maxWidth: '400px'
            }} 
            onClick={e => e.stopPropagation()}
          >
            <h3 style={{ 
              marginBottom: '16px', 
              fontSize: '20px', 
              fontWeight: '600', 
              textAlign: 'center',
              color: '#111827'
            }}>
              {t('profile.examCountryLabel')}
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {EXAM_COUNTRIES.map(c => (
                <button
                  key={c.value}
                  style={{
                    padding: '16px',
                    borderRadius: '12px',
                    border: c.value === examCountry ? '2px solid #059669' : '1px solid #e5e7eb',
                    background: c.value === examCountry ? '#ecfdf5' : '#fff',
                    fontWeight: c.value === examCountry ? '600' : '500',
                    fontSize: '16px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    textAlign: 'left'
                  }}
                  onClick={() => {
                    setExamCountry(c.value)
                    setShowCountrySelect(false)
                    if (userId) updateUserAndCache(userId, { exam_country: c.value }).catch(console.error)
                  }}
                >
                  {c.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Language Selection Modal */}
      {showLanguageSelect && (
        <div 
          style={{ 
            position: 'fixed', 
            top: 0, 
            left: 0, 
            width: '100vw', 
            height: '100vh', 
            background: 'rgba(0,0,0,0.5)', 
            zIndex: 1000, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            padding: '20px'
          }} 
          onClick={() => setShowLanguageSelect(false)}
        >
          <div 
            style={{ 
              background: 'white', 
              borderRadius: '16px', 
              padding: '24px',
              width: '100%',
              maxWidth: '400px'
            }} 
            onClick={e => e.stopPropagation()}
          >
            <h3 style={{ 
              marginBottom: '16px', 
              fontSize: '20px', 
              fontWeight: '600', 
              textAlign: 'center',
              color: '#111827'
            }}>
              {t('profile.examLanguageLabel')}
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {EXAM_LANGUAGES.map(l => (
                <button
                  key={l.value}
                  style={{
                    padding: '16px',
                    borderRadius: '12px',
                    border: l.value === examLanguage ? '2px solid #2563eb' : '1px solid #e5e7eb',
                    background: l.value === examLanguage ? '#eff6ff' : '#fff',
                    fontWeight: l.value === examLanguage ? '600' : '500',
                    fontSize: '16px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    textAlign: 'left'
                  }}
                  onClick={() => {
                    setExamLanguage(l.value)
                    setShowLanguageSelect(false)
                    if (userId) updateUserAndCache(userId, { exam_language: l.value }).catch(console.error)
                  }}
                >
                  {l.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <BottomNavigation />
    </div>
  )
}

export default Profile
