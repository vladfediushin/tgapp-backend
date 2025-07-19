// src/pages/ModeSelect.tsx
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession } from '../store/session'
import { useTranslation } from 'react-i18next'
import { ArrowLeft, Play, Settings, Brain, X, Check, RefreshCw, Sparkles, AlertTriangle } from 'lucide-react'
import BottomNavigation from '../components/BottomNavigation'

const ModeSelect = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const topics = useSession(state => state.cachedTopics || [])

  const [mode, setMode] = useState('interval_all')
  const [batchSize, setBatchSize] = useState(30)
  const [showTopicsModal, setShowTopicsModal] = useState(false)
  const [selectedTopics, setSelectedTopics] = useState([])

  const handleNext = () => {
    const realMode = selectedTopics.length > 0 ? 'topics' : mode
    const params = new URLSearchParams({
      mode: realMode,
      batchSize: String(batchSize),
    })
    selectedTopics.forEach(topic => params.append('topic', topic))
    navigate(
      `/repeat?${params.toString()}`,
      { state: { batchSize, selectedTopics } }
    )
  }

  const toggleTopic = (topic: string) => {
    setSelectedTopics(prev =>
      prev.includes(topic)
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    )
  }

  const modeOptions = [
    { 
      id: 'interval_all', 
      icon: RefreshCw, 
      color: '#2563eb',
      bgColor: '#eff6ff',
      borderColor: '#2563eb'
    },
    { 
      id: 'new_only', 
      icon: Sparkles, 
      color: '#059669',
      bgColor: '#ecfdf5',
      borderColor: '#059669'
    },
    { 
      id: 'incorrect', 
      icon: AlertTriangle, 
      color: '#dc2626',
      bgColor: '#fef2f2',
      borderColor: '#dc2626'
    }
  ]

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
          justifyContent: 'flex-end',
          marginBottom: '32px'
        }}>
          <button
            onClick={() => setShowTopicsModal(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 16px',
              backgroundColor: 'white',
              borderRadius: '12px',
              boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
              border: '1px solid #e5e7eb',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.target.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            }}
            onMouseLeave={(e) => {
              e.target.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
            }}
          >
            <Brain size={16} style={{ color: '#2563eb' }} />
            <span style={{ fontWeight: '500', color: '#374151' }}>
              {selectedTopics.length > 0 
                ? `${selectedTopics.length} ${t('modeSelect.topicsSelected')}`
                : t('modeSelect.topicsAll')
              }
            </span>
          </button>
        </div>

        {/* Title */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{
            fontSize: '28px',
            fontWeight: 'bold',
            color: '#111827',
            margin: '0 0 8px 0'
          }}>
            {t('modeSelect.title')}
          </h1>
          <p style={{ 
            color: '#6b7280',
            margin: 0,
            fontSize: '16px'
          }}>
            {t('modeSelect.subtitle')}
          </p>
        </div>

        {/* Mode Selection */}
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '16px', 
          marginBottom: '32px' 
        }}>
          {modeOptions.map(option => {
            const isSelected = mode === option.id
            const IconComponent = option.icon
            
            return (
              <button
                key={option.id}
                onClick={() => setMode(option.id)}
                style={{
                  width: '100%',
                  padding: '20px',
                  borderRadius: '16px',
                  border: `2px solid ${isSelected ? option.borderColor : '#e5e7eb'}`,
                  backgroundColor: isSelected ? option.bgColor : 'white',
                  boxShadow: isSelected 
                    ? '0 4px 6px -1px rgba(0, 0, 0, 0.1)' 
                    : '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  textAlign: 'left'
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) {
                    e.target.style.borderColor = '#9ca3af'
                    e.target.style.backgroundColor = '#f9fafb'
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) {
                    e.target.style.borderColor = '#e5e7eb'
                    e.target.style.backgroundColor = 'white'
                  }
                }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px'
                }}>
                  <div style={{
                    padding: '12px',
                    borderRadius: '12px',
                    backgroundColor: isSelected ? option.color + '20' : '#f3f4f6',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <IconComponent 
                      size={24} 
                      style={{ color: isSelected ? option.color : '#6b7280' }} 
                    />
                  </div>
                  <div style={{ flex: 1 }}>
                    <h3 style={{
                      fontSize: '18px',
                      fontWeight: '600',
                      color: isSelected ? option.color : '#111827',
                      margin: '0 0 4px 0'
                    }}>
                      {t(`modeSelect.modes.${option.id}`)}
                    </h3>
                    <p style={{
                      fontSize: '14px',
                      color: '#6b7280',
                      margin: 0,
                      lineHeight: '1.4'
                    }}>
                      {t(`modeSelect.modes.${option.id}_desc`)}
                    </p>
                  </div>
                  <div style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: '50%',
                    border: `2px solid ${isSelected ? option.color : '#d1d5db'}`,
                    backgroundColor: isSelected ? option.color : 'transparent',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    {isSelected && (
                      <div style={{
                        width: '8px',
                        height: '8px',
                        backgroundColor: 'white',
                        borderRadius: '50%'
                      }} />
                    )}
                  </div>
                </div>
              </button>
            )
          })}
        </div>

        {/* Batch Size */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '24px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          border: '1px solid #f3f4f6',
          marginBottom: '32px'
        }}>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827',
            marginBottom: '16px',
            margin: '0 0 16px 0'
          }}>
            {t('modeSelect.batchSize')}: <span style={{ color: '#2563eb' }}>{batchSize}</span>
          </h3>
          <input
            type="range"
            min={1}
            max={50}
            value={batchSize}
            onChange={e => setBatchSize(+e.target.value)}
            style={{
              width: '100%',
              height: '8px',
              backgroundColor: '#e5e7eb',
              borderRadius: '4px',
              appearance: 'none',
              cursor: 'pointer',
              outline: 'none'
            }}
          />
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: '14px',
            color: '#6b7280',
            marginTop: '8px'
          }}>
            <span>1</span>
            <span>50</span>
          </div>
        </div>

        {/* Start Button */}
        <button
          onClick={handleNext}
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
          <Play size={20} />
          {t('modeSelect.next')}
        </button>
      </div>

      {/* Topics Modal */}
      {showTopicsModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '16px',
          zIndex: 50
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '24px',
            width: '100%',
            maxWidth: '400px',
            maxHeight: '80vh',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '24px'
            }}>
              <h3 style={{
                fontSize: '20px',
                fontWeight: 'bold',
                color: '#111827',
                margin: 0
              }}>
                {t('modeSelect.modal.title')}
              </h3>
              <button
                onClick={() => setShowTopicsModal(false)}
                style={{
                  padding: '8px',
                  backgroundColor: 'transparent',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = '#f3f4f6'
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = 'transparent'
                }}
              >
                <X size={20} style={{ color: '#6b7280' }} />
              </button>
            </div>
            
            <div style={{
              flex: 1,
              overflowY: 'auto',
              marginBottom: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}>
              {[...topics]
                .sort((a, b) => {
                  const numA = parseInt(a.match(/\d+/)?.[0] || '', 10)
                  const numB = parseInt(b.match(/\d+/)?.[0] || '', 10)
                  if (!isNaN(numA) && !isNaN(numB)) return numA - numB
                  return a.localeCompare(b, 'ru')
                })
                .map(topic => (
                  <label 
                    key={topic} 
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      padding: '12px',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.backgroundColor = '#f9fafb'
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.backgroundColor = 'transparent'
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedTopics.includes(topic)}
                      onChange={() => toggleTopic(topic)}
                      style={{
                        width: '20px',
                        height: '20px',
                        accentColor: '#2563eb',
                        borderRadius: '4px'
                      }}
                    />
                    <span style={{ 
                      color: '#374151',
                      fontSize: '15px'
                    }}>
                      {topic}
                    </span>
                  </label>
                ))}
            </div>
            
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => setShowTopicsModal(false)}
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  backgroundColor: '#f3f4f6',
                  color: '#374151',
                  borderRadius: '12px',
                  border: 'none',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = '#e5e7eb'
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = '#f3f4f6'
                }}
              >
                <X size={16} />
                {t('modeSelect.modal.cancel')}
              </button>
              <button
                onClick={() => {
                  setMode('topics')
                  setShowTopicsModal(false)
                }}
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  backgroundColor: '#2563eb',
                  color: 'white',
                  borderRadius: '12px',
                  border: 'none',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = '#1d4ed8'
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = '#2563eb'
                }}
              >
                <Check size={16} />
                {t('modeSelect.modal.confirm')}
              </button>
            </div>
          </div>
        </div>
      )}

      <BottomNavigation />
    </div>
  )
}

export default ModeSelect
