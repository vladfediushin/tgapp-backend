// src/pages/Authorize.tsx
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createUser, UserOut as ApiUserOut } from '../api/api'
import { useSession, updateUserAndCache, loadTopicsWithCache, loadUserWithCache } from '../store/session'
import { AxiosError } from 'axios'
import { useTranslation } from 'react-i18next'
import i18n from 'i18next'
import LoadingSpinner from '../components/LoadingSpinner'
import CustomSelect from '../components/CustomSelect'
import { UserCheck, Globe, MapPin, Languages } from 'lucide-react'

// Список стран
const EXAM_COUNTRIES = [
  { value: 'am', label: '🇦🇲 Армения' },
  { value: 'kz', label: '🇰🇿 Казахстан' },
  { value: 'by', label: '🇧🇾 Беларусь' },
]

// Языки экзамена и интерфейса
const EXAM_LANGUAGES = [
  { value: 'ru', label: 'Русский' },
  { value: 'en', label: 'English' },
]
const UI_LANGUAGES = [
  { value: 'ru', label: 'Русский' },
  { value: 'en', label: 'English' },
]

const Authorize = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  // для этой страницы: подтягиваем языковой код из Telegram и ставим дефолт
  const tgUserInit = window.Telegram?.WebApp?.initDataUnsafe?.user
  const rawLang = tgUserInit?.language_code?.split('-')[0] ?? ''
  const hasLang = UI_LANGUAGES.some(l => l.value === rawLang)
  const defaultUiLang = hasLang ? rawLang : 'en'

  // экшены стора
  const setInternalId        = useSession(state => state.setUserId)
  const setCachedUser        = useSession(state => state.setCachedUser)
  const setStoreExamCountry  = useSession(state => state.setExamCountry)
  const setStoreExamLanguage = useSession(state => state.setExamLanguage)
  const setStoreUiLanguage   = useSession(state => state.setUiLanguage)

  const [step, setStep]         = useState('checking')
  const [userName, setUserName] = useState('друг')

  // локальные стейты для формы
  const [examCountryInput, setExamCountryInput]   = useState('')
  const [examLanguageInput, setExamLanguageInput] = useState('')
  const [uiLanguageInput, setUiLanguageInput]     = useState(defaultUiLang)

  const [error, setError] = useState('')

  // меняем язык i18next на тот, что из Telegram (или en), и затем при выборе в форме
  useEffect(() => {
    i18n.changeLanguage(uiLanguageInput)
  }, [uiLanguageInput])

  // Первый эффект: проверяем, есть ли пользователь в БД
  useEffect(() => {
    const init = async () => {
      const tg = window.Telegram?.WebApp
      const tgUser = tg?.initDataUnsafe?.user
      if (!tg || !tgUser) {
        setStep('complete')
        return
      }

      tg.ready()
      tg.expand()
      setUserName(tgUser.first_name || 'друг')

      try {
        const user = await loadUserWithCache(tgUser.id)

        // Данные уже кешированы в loadUserWithCache, просто обновляем локальные стейты
        setInternalId(user.id)
        setStoreExamCountry(user.exam_country  ?? '')
        setStoreExamLanguage(user.exam_language ?? '')
        setStoreUiLanguage(user.ui_language     ?? '')

        // загружаем темы с кешированием (уже сохраняется в кеш автоматически)
        await loadTopicsWithCache(
          user.exam_country  ?? '',
          user.exam_language ?? ''
        )

        // переходим на Home - existing user
        setStep('complete')
      } catch (err) {
        const axiosErr = err as AxiosError
        if (axiosErr.response?.status === 404) {
          // New user - show form
          setStep('form')
        } else {
          setError(t('authorize.error.checkUser'))
          setStep('form')
        }
      }
    }
    init()
  }, [
    t,
    setInternalId,
    setStoreExamCountry,
    setStoreExamLanguage,
    setStoreUiLanguage,
  ])

  // Когда step становится complete — делаем navigate
  useEffect(() => {
    if (step === 'complete') {
      navigate('/home', { replace: true })
    }
  }, [step, navigate])

  const handleSubmit = async () => {
    if (!examCountryInput || !examLanguageInput || !uiLanguageInput) {
      setError(t('authorize.error.requiredFields'))
      return
    }
    setError('')

    const tg = window.Telegram?.WebApp
    const tgUser = tg?.initDataUnsafe?.user
    if (!tgUser) {
      setError(t('authorize.error.telegramData'))
      setStep('form')
      return
    }

    try {
      const res = await createUser({
        telegram_id: tgUser.id,
        username: tgUser.username || undefined,
        first_name: tgUser.first_name || undefined,
        last_name: tgUser.last_name || undefined,
        exam_country: examCountryInput,
        exam_language: examLanguageInput,
        ui_language: uiLanguageInput,
        // exam_date and daily_goal are optional - will be set in next step
      })

      setInternalId(res.data.id)
      setStoreExamCountry(res.data.exam_country  ?? '')
      setStoreExamLanguage(res.data.exam_language ?? '')
      setStoreUiLanguage(res.data.ui_language     ?? '')

      // подтягиваем темы с кешированием (уже сохраняется в кеш автоматически)
      await loadTopicsWithCache(
        res.data.exam_country  ?? '',
        res.data.exam_language ?? ''
      )

      // Новый пользователь создан - переходим сразу на домашнюю страницу
      setStep('complete')
    } catch {
      setError(t('authorize.error.createUser'))
      setStep('form')
    }
  }



  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%)',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {step === 'checking' && (
        <LoadingSpinner 
          size={80} 
          text={t('authorize.checking')} 
          fullScreen 
        />
      )}

      {step === 'form' && (
        <div style={{
          flex: 1,
          padding: '24px',
          paddingBottom: '24px',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{
            maxWidth: '352px', // 375 - 24*2 = 327, но 352px для чуть большего экрана
            width: '100%',
            margin: '0 auto',
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            boxSizing: 'border-box',
          }}>
            {/* Welcome Header */}
            <div style={{
              textAlign: 'center',
              marginBottom: '32px'
            }}>
              <div style={{
                backgroundColor: 'white',
                borderRadius: '50%',
                padding: '12px',
                width: '56px',
                height: '56px',
                margin: '0 auto 24px',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <UserCheck size={28} style={{ color: '#2563eb' }} />
              </div>
              <h1 style={{
                fontSize: '30px',
                fontWeight: 'bold',
                color: '#111827',
                marginBottom: '8px'
              }}>
                {t('authorize.welcome', { userName })}
              </h1>
              <p style={{
                color: '#6b7280',
                lineHeight: '1.6'
              }}>
                {t('authorize.intro')}
              </p>
            </div>

            {/* Form */}
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '24px'
            }}>
              {/* Exam Country */}
              <div>
                <label style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#374151',
                  marginBottom: '12px'
                }}>
                  <MapPin size={16} style={{ color: '#2563eb' }} />
                  {t('authorize.label.examCountry')}
                </label>
                <CustomSelect
                  value={examCountryInput}
                  onChange={setExamCountryInput}
                  options={EXAM_COUNTRIES}
                  placeholder={t('authorize.placeholder.selectCountry')}
                  icon={<MapPin size={16} style={{ color: '#2563eb' }} />}
                />
              </div>

              {/* Exam Language */}
              <div>
                <label style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#374151',
                  marginBottom: '12px'
                }}>
                  <Languages size={16} style={{ color: '#2563eb' }} />
                  {t('authorize.label.examLanguage')}
                </label>
                <CustomSelect
                  value={examLanguageInput}
                  onChange={setExamLanguageInput}
                  options={EXAM_LANGUAGES}
                  placeholder={t('authorize.placeholder.selectLanguage')}
                  icon={<Languages size={16} style={{ color: '#2563eb' }} />}
                />
              </div>

              {/* UI Language */}
              <div>
                <label style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#374151',
                  marginBottom: '12px'
                }}>
                  <Globe size={16} style={{ color: '#2563eb' }} />
                  {t('authorize.label.uiLanguage')}
                </label>
                <CustomSelect
                  value={uiLanguageInput}
                  onChange={setUiLanguageInput}
                  options={UI_LANGUAGES}
                  placeholder={t('authorize.placeholder.selectLanguage')}
                  icon={<Globe size={16} style={{ color: '#2563eb' }} />}
                />
              </div>
            </div>

            {/* Button Container with fixed spacing */}
            <div style={{
              marginTop: '48px',
              position: 'relative'
            }}>
              {/* Error Message - positioned above button */}
              {error && (
                <div style={{
                  position: 'absolute',
                  top: '-40px',
                  left: 0,
                  right: 0,
                  padding: '12px 16px',
                  backgroundColor: '#fef2f2',
                  border: '1px solid #fecaca',
                  borderRadius: '8px',
                  zIndex: 10
                }}>
                  <p style={{
                    color: '#b91c1c',
                    fontSize: '14px',
                    margin: 0,
                    textAlign: 'center'
                  }}>{error}</p>
                </div>
              )}

              {/* Submit Button */}
              <button
                onClick={handleSubmit}
                style={{
                  width: '100%',
                  background: 'linear-gradient(135deg, #2563eb 0%, #4f46e5 100%)',
                  color: 'white',
                  padding: '16px 24px',
                  borderRadius: '12px',
                  fontWeight: '600',
                  fontSize: '18px',
                  border: 'none',
                  cursor: 'pointer',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.target.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
                  e.target.style.transform = 'translateY(-1px)'
                }}
                onMouseLeave={(e) => {
                  e.target.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                  e.target.style.transform = 'translateY(0)'
                }}
              >
                {t('authorize.button.next')}
              </button>
            </div>

            {/* Footer Info */}
            <p style={{
              marginTop: '24px',
              fontSize: '14px',
              color: '#9ca3af',
              textAlign: 'center',
              lineHeight: '1.6'
            }}>
              {t('authorize.footer.info')}
            </p>
          </div>
        </div>
      )}

      {step === 'complete' && (
        <LoadingSpinner 
          size={80} 
          text={t('authorize.checking')} 
          fullScreen 
        />
      )}
    </div>
  )
}

export default Authorize
