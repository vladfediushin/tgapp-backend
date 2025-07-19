// QuestionCard.tsx - Modern question card component
import React from 'react'
import { CheckCircle, XCircle } from 'lucide-react'

interface QuestionCardProps {
  question: string
  options: string[]
  questionImage?: string
  selectedIndex?: number | null
  correctIndex: number
  isAnswered: boolean
  onAnswerSelect: (index: number) => void
}

const QuestionCard = ({
  question,
  options,
  questionImage,
  selectedIndex,
  correctIndex,
  isAnswered,
  onAnswerSelect
}: QuestionCardProps) => {
  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '16px',
      padding: '24px',
      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
    }}>
      <h2 style={{
        fontSize: '18px',
        fontWeight: '600',
        color: '#111827',
        marginBottom: '16px',
        margin: 0
      }}>
        Вопрос
      </h2>
      
      {questionImage && (
        <div style={{ marginBottom: '16px' }}>
          <img
            src={questionImage}
            alt="question"
            style={{ 
              width: '100%', 
              maxWidth: '400px',
              height: 'auto',
              borderRadius: '12px',
              display: 'block',
              margin: '0 auto'
            }}
          />
        </div>
      )}
      
      <p style={{ 
        fontSize: '16px', 
        lineHeight: '1.5',
        color: '#374151',
        margin: '0 0 20px 0'
      }}>
        {question}
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {options.map((opt, idx) => {
          let backgroundColor = 'white'
          let borderColor = '#d1d5db'
          let color = '#374151'
          
          if (isAnswered) {
            if (idx === selectedIndex) {
              if (idx === correctIndex) {
                backgroundColor = '#ecfdf5'
                borderColor = '#059669'
                color = '#059669'
              } else {
                backgroundColor = '#fef2f2'
                borderColor = '#dc2626'
                color = '#dc2626'
              }
            } else if (idx === correctIndex) {
              backgroundColor = '#ecfdf5'
              borderColor = '#059669'
              color = '#059669'
            }
          }

          const maybeUrl = opt.replace(/[{}]/g, '').trim()
          const isImage = /\.(jpe?g|png|gif|webp)$/i.test(maybeUrl)

          return (
            <button
              key={idx}
              onClick={() => onAnswerSelect(idx)}
              disabled={isAnswered}
              style={{
                width: '100%',
                padding: '16px',
                border: `2px solid ${borderColor}`,
                borderRadius: '12px',
                backgroundColor,
                color,
                textAlign: 'left',
                cursor: isAnswered ? 'default' : 'pointer',
                transition: 'all 0.2s ease',
                position: 'relative',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}
              onMouseEnter={(e) => {
                if (!isAnswered) {
                  e.target.style.borderColor = '#6b7280'
                  e.target.style.backgroundColor = '#f9fafb'
                }
              }}
              onMouseLeave={(e) => {
                if (!isAnswered) {
                  e.target.style.borderColor = '#d1d5db'
                  e.target.style.backgroundColor = 'white'
                }
              }}
            >
              <div style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor: isAnswered && (idx === selectedIndex || idx === correctIndex) 
                  ? (idx === correctIndex) 
                    ? '#059669' 
                    : '#dc2626'
                  : '#e5e7eb',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}>
                {isAnswered && (idx === selectedIndex || idx === correctIndex) ? (
                  idx === correctIndex ? (
                    <CheckCircle size={16} style={{ color: 'white' }} />
                  ) : (
                    <XCircle size={16} style={{ color: 'white' }} />
                  )
                ) : (
                  <span style={{ 
                    color: '#6b7280', 
                    fontSize: '12px', 
                    fontWeight: 'bold' 
                  }}>
                    {idx + 1}
                  </span>
                )}
              </div>
              
              <div style={{ flex: 1 }}>
                {isImage ? (
                  <img
                    src={maybeUrl}
                    alt={`option ${idx + 1}`}
                    style={{ 
                      maxWidth: '120px', 
                      height: 'auto', 
                      borderRadius: '8px',
                      display: 'block'
                    }}
                  />
                ) : (
                  <span style={{ 
                    fontSize: '15px',
                    lineHeight: '1.4',
                    fontWeight: '500'
                  }}>
                    {opt}
                  </span>
                )}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default QuestionCard
