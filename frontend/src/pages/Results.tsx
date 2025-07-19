// frontend/src/pages/Results.tsx
import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession } from '../store/session'
import { useTranslation } from 'react-i18next'
import { Trophy, CheckCircle, XCircle, ArrowLeft, RotateCcw, Home } from 'lucide-react'
import BottomNavigation from '../components/BottomNavigation'
import { backgroundSyncStats } from '../utils/statsSync'

const Results = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const answers = useSession(state => state.answers)
  const userId = useSession(state => state.userId)
  const location = window.location
  const state = (location as any).state || {}

  // Background sync stats after quiz completion
  useEffect(() => {
    if (userId && answers.length > 0) {
      // Run background sync without blocking UI
      backgroundSyncStats(userId)
        .then(result => {
          if (result.success) {
            console.log('📊 Stats synced successfully in background')
          }
        })
        .catch(error => {
          console.error('Background sync error:', error)
        })
    }
  }, [userId]) // Only run once when component mounts

  // Try to get state from react-router if available
  let noQuestions = false
  try {
    // @ts-ignore
    if (window.history.state && window.history.state.usr && window.history.state.usr.noQuestions) {
      noQuestions = true
    }
  } catch {}

  // Fallback for react-router v6
  if (typeof window !== 'undefined' && window.history && window.history.state && window.history.state.usr) {
    noQuestions = window.history.state.usr.noQuestions || false
  }

  const answersMap = new Map()
  answers.forEach(a => {
    if (!answersMap.has(a.questionId)) {
      answersMap.set(a.questionId, a)
    }
  })
  const uniqueAnswers = Array.from(answersMap.values())
  const correct = uniqueAnswers.filter(a => a.isCorrect).length
  const incorrect = uniqueAnswers.length - correct
  const percentage = uniqueAnswers.length > 0 ? Math.round((correct / uniqueAnswers.length) * 100) : 0

  const getScoreColor = () => {
    if (percentage >= 80) return '#059669'
    if (percentage >= 60) return '#d97706'
    return '#dc2626'
  }

  const getScoreMessage = () => {
    if (percentage >= 90) return t('results.excellent')
    if (percentage >= 80) return t('results.good')
    if (percentage >= 60) return t('results.fair')
    return t('results.needsImprovement')
  }

  const handleTryAgain = () => {
    navigate('/mode')
  }

  const handleReviewIncorrect = () => {
    const params = new URLSearchParams({
      mode: 'incorrect',
      batchSize: '30',
    })
    navigate(`/repeat?${params.toString()}`)
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f8fafc', 
      paddingBottom: '80px' 
    }}>
      <div style={{ padding: '24px' }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '32px'
        }}>
          <button
            onClick={() => navigate('/')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 16px',
              backgroundColor: 'transparent',
              border: 'none',
              borderRadius: '8px',
              color: '#6b7280',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = '#f3f4f6'
              e.target.style.color = '#111827'
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'transparent'
              e.target.style.color = '#6b7280'
            }}
          >
            <ArrowLeft size={20} />
            <span style={{ fontWeight: '500' }}>Назад</span>
          </button>
        </div>

        {/* Results Card */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '32px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          border: '1px solid #f3f4f6',
          marginBottom: '24px'
        }}>
          {/* Trophy Icon */}
          <div style={{ textAlign: 'center', marginBottom: '24px' }}>
            <div style={{
              background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
              borderRadius: '50%',
              padding: '16px',
              width: '80px',
              height: '80px',
              margin: '0 auto 16px auto',
              boxShadow: '0 10px 25px -3px rgba(251, 191, 36, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Trophy size={40} style={{ color: 'white' }} />
            </div>
            <h1 style={{
              fontSize: '28px',
              fontWeight: 'bold',
              color: '#111827',
              margin: '0 0 8px 0'
            }}>
              {t('results.sessionComplete')}
            </h1>
            <p style={{ 
              color: '#6b7280',
              margin: 0,
              fontSize: '16px'
            }}>
              {getScoreMessage()}
            </p>
          </div>

          {noQuestions ? (
            <div style={{
              textAlign: 'center',
              padding: '24px',
              backgroundColor: '#fef2f2',
              borderRadius: '12px',
              border: '1px solid #fecaca'
            }}>
              <XCircle size={48} style={{ 
                color: '#dc2626', 
                margin: '0 auto 16px auto',
                display: 'block'
              }} />
              <p style={{
                color: '#dc2626',
                fontWeight: '600',
                fontSize: '18px',
                margin: 0
              }}>
                {t('results.noQuestions')}
              </p>
            </div>
          ) : (
            <>
              {/* Score Circle */}
              <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                <div style={{
                  position: 'relative',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <svg 
                    width="128" 
                    height="128" 
                    style={{ transform: 'rotate(-90deg)' }}
                    viewBox="0 0 100 100"
                  >
                    <circle
                      cx="50"
                      cy="50"
                      r="45"
                      stroke="#e5e7eb"
                      strokeWidth="8"
                      fill="transparent"
                    />
                    <circle
                      cx="50"
                      cy="50"
                      r="45"
                      stroke={getScoreColor()}
                      strokeWidth="8"
                      fill="transparent"
                      strokeDasharray={`${percentage * 2.83} 283`}
                      strokeLinecap="round"
                      style={{ transition: 'all 1s ease-out' }}
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
                      fontSize: '24px',
                      fontWeight: 'bold',
                      color: getScoreColor()
                    }}>
                      {percentage}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Stats */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr 1fr',
                gap: '16px',
                marginBottom: '24px'
              }}>
                <div style={{
                  textAlign: 'center',
                  padding: '16px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '12px'
                }}>
                  <div style={{
                    fontSize: '24px',
                    fontWeight: 'bold',
                    color: '#111827'
                  }}>
                    {uniqueAnswers.length}
                  </div>
                  <div style={{
                    fontSize: '14px',
                    color: '#6b7280'
                  }}>
                    Всего
                  </div>
                </div>
                <div style={{
                  textAlign: 'center',
                  padding: '16px',
                  backgroundColor: '#ecfdf5',
                  borderRadius: '12px'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '4px',
                    marginBottom: '4px'
                  }}>
                    <CheckCircle size={16} style={{ color: '#059669' }} />
                    <div style={{
                      fontSize: '24px',
                      fontWeight: 'bold',
                      color: '#059669'
                    }}>
                      {correct}
                    </div>
                  </div>
                  <div style={{
                    fontSize: '14px',
                    color: '#6b7280'
                  }}>
                    Верных
                  </div>
                </div>
                <div style={{
                  textAlign: 'center',
                  padding: '16px',
                  backgroundColor: '#fef2f2',
                  borderRadius: '12px'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '4px',
                    marginBottom: '4px'
                  }}>
                    <XCircle size={16} style={{ color: '#dc2626' }} />
                    <div style={{
                      fontSize: '24px',
                      fontWeight: 'bold',
                      color: '#dc2626'
                    }}>
                      {incorrect}
                    </div>
                  </div>
                  <div style={{
                    fontSize: '14px',
                    color: '#6b7280'
                  }}>
                    Ошибок
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Action Buttons */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <button
              onClick={handleTryAgain}
              style={{
                width: '100%',
                background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                color: 'white',
                padding: '16px 24px',
                borderRadius: '16px',
                border: 'none',
                fontSize: '18px',
                fontWeight: '600',
                boxShadow: '0 4px 6px -1px rgba(5, 150, 105, 0.3)',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '12px'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-1px)'
                e.target.style.boxShadow = '0 8px 15px -3px rgba(5, 150, 105, 0.4)'
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)'
                e.target.style.boxShadow = '0 4px 6px -1px rgba(5, 150, 105, 0.3)'
              }}
            >
              <RotateCcw size={20} />
              Попробовать снова
            </button>
            
            {incorrect > 0 && (
              <button
                onClick={handleReviewIncorrect}
                style={{
                  width: '100%',
                  backgroundColor: '#dc2626',
                  color: 'white',
                  padding: '12px 24px',
                  borderRadius: '12px',
                  border: 'none',
                  fontSize: '16px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '12px'
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = '#b91c1c'
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = '#dc2626'
                }}
              >
                <XCircle size={18} />
                Повторить ошибки
              </button>
            )}
            
            <button
              onClick={() => navigate('/')}
              style={{
                width: '100%',
                backgroundColor: '#f3f4f6',
                color: '#374151',
                padding: '12px 24px',
                borderRadius: '12px',
                border: 'none',
                fontSize: '16px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '12px'
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = '#e5e7eb'
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = '#f3f4f6'
              }}
            >
              <Home size={18} />
              На главную
            </button>
          </div>
        </div>
      </div>

      <BottomNavigation />
    </div>
  )
}

export default Results