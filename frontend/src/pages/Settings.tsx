import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession, updateUserAndCache } from '../store/session'
import { updateUser } from '../api/api'
import { useTranslation } from 'react-i18next'
import HomeButton from '../components/HomeButton'
import BottomNavigation from '../components/BottomNavigation'
import ExamSettingsComponent from '../components/ExamSettingsComponent'
import { Globe, ChevronDown, Calendar } from 'lucide-react'
import i18n from 'i18next'

const UI_LANGUAGES = [
  { value: 'ru', label: '🇷🇺 Русский' },
  { value: 'en', label: '🇺🇸 English' },
]

const Settings = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  
  const userId = useSession(state => state.userId)
  const uiLanguage = useSession(state => state.uiLanguage)
  const setUiLanguage = useSession(state => state.setUiLanguage)

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
            {t('settings.title')}
          </h1>
        </div>
      </div>

      <div style={{ padding: '24px', gap: '24px', display: 'flex', flexDirection: 'column' }}>
        {/* Language Settings Card */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '24px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '20px'
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              backgroundColor: '#dbeafe',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Globe size={20} color="#2563eb" />
            </div>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#111827',
              margin: 0
            }}>
              Язык интерфейса
            </h2>
          </div>

          <div style={{
            position: 'relative'
          }}>
            <select
              value={uiLanguage}
              onChange={e => {
                const newUi = e.target.value
                setUiLanguage(newUi)
                i18n.changeLanguage(newUi)
                if (userId) {
                  updateUserAndCache(userId, { ui_language: newUi }).catch(err =>
                    console.error('Ошибка обновления языка интерфейса:', err)
                  )
                }
              }}
              style={{ 
                width: '100%',
                padding: '16px',
                paddingRight: '48px',
                borderRadius: '12px',
                border: '1px solid #d1d5db',
                fontSize: '16px',
                backgroundColor: 'white',
                appearance: 'none',
                cursor: 'pointer',
                outline: 'none',
                transition: 'all 0.2s ease'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#2563eb'
                e.target.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)'
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#d1d5db'
                e.target.style.boxShadow = 'none'
              }}
            >
              {UI_LANGUAGES.map(l => (
                <option key={l.value} value={l.value}>
                  {l.label}
                </option>
              ))}
            </select>
            <div style={{
              position: 'absolute',
              right: '16px',
              top: '50%',
              transform: 'translateY(-50%)',
              pointerEvents: 'none'
            }}>
              <ChevronDown size={20} color="#6b7280" />
            </div>
          </div>
          
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            margin: '12px 0 0 0'
          }}>
            Выберите предпочитаемый язык для интерфейса приложения
          </p>
        </div>

        {/* Exam Settings Card */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '24px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '20px'
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              backgroundColor: '#fef3c7',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Calendar size={20} color="#d97706" />
            </div>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#111827',
              margin: 0
            }}>
              Настройки экзамена
            </h2>
          </div>

          <ExamSettingsComponent 
            showTitle={false} 
            compact={true}
          />
        </div>
      </div>

      <BottomNavigation />
    </div>
  )
}

export default Settings
