// src/components/ExamSettingsComponent.tsx
import React, { useState, useEffect } from 'react'
import { useSession, setExamSettingsAndCache, loadExamSettingsWithCache, loadRemainingCountWithCache } from '../store/session'
import { ExamSettingsResponse, ExamSettingsUpdate } from '../api/api'
import ReactDatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'

interface ExamSettingsComponentProps {
  showTitle?: boolean  // Whether to show the "Exam Settings" title
  onSave?: (settings: ExamSettingsResponse) => void  // Callback when settings are saved
  compact?: boolean    // Whether to use compact layout
}

// Вместо React.FC используем обычную функцию
function ExamSettingsComponent({ 
  showTitle = true, 
  onSave,
  compact = false 
}: ExamSettingsComponentProps) {
  const userId = useSession(state => state.userId)
  const examCountry = useSession(state => state.examCountry)
  const examLanguage = useSession(state => state.examLanguage)
  
  // Get initial values from session store
  const sessionExamDate = useSession(state => state.examDate)
  const sessionDailyGoal = useSession(state => state.manualDailyGoal)
  
  // Исправляем типизацию useState для совместимости с React 19+
  const [settings, setSettingsState] = useState(null)
  const [examDate, setExamDate] = useState(sessionExamDate || '')
  const [dailyGoal, setDailyGoal] = useState(sessionDailyGoal || 10)
  const [recommendedGoal, setRecommendedGoal] = useState(null)
  const [remainingQuestions, setRemainingQuestions] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  // Update local state when session store values change
  useEffect(() => {
    if (sessionExamDate !== null) {
      setExamDate(sessionExamDate || '')
    }
  }, [sessionExamDate])
  
  useEffect(() => {
    if (sessionDailyGoal !== null) {
      setDailyGoal(sessionDailyGoal || 10)
    }
  }, [sessionDailyGoal])

  useEffect(() => {
    loadSettings()
  }, [userId])

  useEffect(() => {
    // Пересчитываем рекомендуемое количество при изменении даты экзамена
    if (examDate && userId && examCountry && examLanguage) {
      calculateRecommendedGoal()
    }
  }, [examDate, userId, examCountry, examLanguage])

  const calculateRecommendedGoal = async () => {
    if (!examDate || !userId || !examCountry || !examLanguage) return

    try {
      // Получаем количество нерешенных вопросов с кешированием
      const remaining = await loadRemainingCountWithCache(userId, examCountry, examLanguage)
      setRemainingQuestions(remaining)

      // Рассчитываем рекомендуемое количество
      const today = new Date()
      const examDateObj = new Date(examDate)
      const totalDays = Math.ceil((examDateObj.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
      
      if (totalDays <= 0) {
        setRecommendedGoal(null)
        return
      }

      // 80% времени на изучение, 20% на повторение
      const studyDays = Math.floor(totalDays * 0.8)
      const recommended = studyDays > 0 ? Math.ceil(remaining / studyDays) : remaining
      
      setRecommendedGoal(recommended)
      
      // Всегда устанавливаем рекомендуемое значение по умолчанию
      setDailyGoal(recommended)
    } catch (err) {
      console.error('Failed to calculate recommended goal:', err)
    }
  }

  const loadSettings = async () => {
    if (!userId) {
      setLoading(false)
      return
    }
    
    try {
      setLoading(true)
      const settingsData = await loadExamSettingsWithCache(userId)
      setSettingsState(settingsData)
      
      if (settingsData.exam_date) {
        setExamDate(settingsData.exam_date)
      }
      if (settingsData.daily_goal) {
        setDailyGoal(settingsData.daily_goal)
      }
    } catch (err) {
      console.error('Failed to load exam settings:', err)
      // Don't show error for missing settings (user hasn't set them yet)
      if (err.response?.status !== 404) {
        setError('Не удалось загрузить настройки экзамена')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!userId) {
      setError('Пользователь не найден')
      return
    }

    // Allow saving even without exam date (optional)
    try {
      setSaving(true)
      setError(null)
      
      const updateData: ExamSettingsUpdate = {
        ...(examDate ? { exam_date: examDate } : {}),
        ...(dailyGoal !== undefined && dailyGoal !== null ? { daily_goal: dailyGoal } : {})
      }
      
      const response = await setExamSettingsAndCache(userId, updateData)
      setSettingsState(response)
      
      // Call the callback if provided
      if (onSave) {
        onSave(response)
      }
      
    } catch (err: any) {
      console.error('Failed to save exam settings:', err)
      const errorMessage = err.response?.data?.detail || 'Ошибка сохранения настроек'
      setError(errorMessage)
    } finally {
      setSaving(false)
    }
  }

  // Преобразуем examDate к Date для DatePicker
  const examDateObj = examDate ? new Date(examDate) : null

  if (loading) {
    return (
      <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
        Загрузка настроек...
      </div>
    )
  }

  const containerStyle = compact ? {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '16px',
    width: '100%'
  } : {
    margin: '0 auto',
    maxWidth: 340,
    background: '#fff',
    borderRadius: 18,
    boxShadow: '0 4px 24px 0 rgba(0,0,0,0.08)',
    padding: 24,
    border: '1px solid #e5e7eb',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    gap: 20,
  }

  return (
    <div style={containerStyle}>
      {showTitle && (
        <h3 style={{ margin: 0, fontSize: 20, fontWeight: 700, textAlign: 'center' }}>
          Настройки экзамена
        </h3>
      )}
      {error && (
        <div style={{ 
          color: 'red', 
          backgroundColor: '#ffebee', 
          padding: 8, 
          borderRadius: 8, 
          marginBottom: 8,
          fontSize: 14,
          width: '100%',
          textAlign: 'center',
        }}>
          {error}
        </div>
      )}
      <div style={{ width: '100%' }}>
        <label style={{ fontWeight: 500, fontSize: 16, marginBottom: 8, display: 'block' }}>
          Дата экзамена:
        </label>
        <ReactDatePicker
          selected={examDateObj}
          onChange={date => setExamDate(date ? date.toISOString().split('T')[0] : '')}
          minDate={new Date()}
          dateFormat="dd/MM/yyyy"
          placeholderText="Выберите дату"
          className="custom-datepicker-input"
          popperPlacement="bottom"
          showPopperArrow={false}
          wrapperClassName="custom-datepicker-wrapper"
          style={{ width: '100%' }}
        />
      </div>
      <div style={{ width: '100%' }}>
        <label style={{ fontWeight: 500, fontSize: 16, marginBottom: 8, display: 'block' }}>
          Ежедневная цель: {dailyGoal} вопросов
        </label>
        {recommendedGoal && remainingQuestions !== null && (
          <div style={{
            fontSize: 13,
            color: '#666',
            marginBottom: 8,
            padding: 8,
            backgroundColor: '#f0f9ff',
            borderRadius: 6,
            border: '1px solid #0ea5e9'
          }}>
            💡 Рекомендуем: <strong>{recommendedGoal} вопросов/день</strong>
            <br />
            Осталось изучить: {remainingQuestions} вопросов
            <br />
            {examDate && (() => {
              const today = new Date()
              const examDateObj = new Date(examDate)
              const totalDays = Math.ceil((examDateObj.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
              const studyDays = Math.floor(totalDays * 0.8)
              return `${studyDays} дней на изучение, ${totalDays - studyDays} дней на повторение`
            })()}
          </div>
        )}
        <input
          type="range"
          min="1"
          max="100"
          value={dailyGoal}
          onChange={e => setDailyGoal(Number(e.target.value))}
          style={{ width: '100%' }}
        />
      </div>
      <button
        onClick={handleSave}
        disabled={saving}
        style={{
          width: '100%',
          padding: 14,
          background: saving ? '#ccc' : 'linear-gradient(90deg,#2AABEE 0%,#4F8EF7 100%)',
          color: 'white',
          border: 'none',
          borderRadius: 10,
          fontSize: 17,
          fontWeight: 600,
          cursor: saving ? 'not-allowed' : 'pointer',
          boxShadow: '0 2px 8px 0 rgba(42,171,238,0.08)'
        }}
      >
        {saving ? 'Сохранение...' : 'Сохранить настройки'}
      </button>
    </div>
  )
}

export default ExamSettingsComponent