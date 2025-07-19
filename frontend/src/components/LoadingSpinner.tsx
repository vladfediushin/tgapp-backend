import { Loader2 } from 'lucide-react'

interface LoadingSpinnerProps {
  size?: number
  color?: string
  text?: string
  fullScreen?: boolean
}

const LoadingSpinner = ({ 
  size = 24, 
  color = '#059669', 
  text,
  fullScreen = false 
}: LoadingSpinnerProps) => {
  const spinnerElement = (
    <>
      <style>
        {`
          @keyframes loading-spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
          .loading-spinner {
            animation: loading-spin 1s linear infinite;
          }
        `}
      </style>
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center',
        gap: text ? '16px' : '0'
      }}>
        <Loader2 
          size={size} 
          color={color}
          className="loading-spinner"
          style={{
            animation: 'loading-spin 1s linear infinite'
          }}
        />
        {text && (
          <p style={{
            color: '#6b7280',
            fontSize: '16px',
            margin: 0,
            textAlign: 'center'
          }}>
            {text}
          </p>
        )}
      </div>
    </>
  )

  if (fullScreen) {
    return (
      <div style={{
        minHeight: '100vh',
        backgroundColor: '#f8fafc',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px'
      }}>
        {spinnerElement}
      </div>
    )
  }

  return spinnerElement
}

export default LoadingSpinner