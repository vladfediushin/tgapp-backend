import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import HomeButton from '../components/HomeButton'
import BottomNavigation from '../components/BottomNavigation'
import ExamSettingsComponent from '../components/ExamSettingsComponent'

const ExamSettings = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const handleSave = () => {
    // Navigate back to profile after saving
    navigate('/profile')
  }

  return (
    <div style={{ 
      padding: 20, 
      minHeight: '100vh', 
      backgroundColor: '#f8fafc', 
      paddingBottom: '80px' 
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 24 }}>
        <HomeButton style={{ marginRight: 16 }} />
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 600 }}>
          {t('examSettings.title')}
        </h1>
      </div>

      {/* Exam Settings Component */}
      <ExamSettingsComponent 
        showTitle={false} 
        compact={false} 
        onSave={handleSave} 
      />

      <BottomNavigation />
    </div>
  )
}

export default ExamSettings
