import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { FaHome } from 'react-icons/fa'

interface HomeButtonProps {
  style?: any
  size?: number
}

const HomeButton = ({ style, size = 24 }: HomeButtonProps) => {
  const navigate = useNavigate()
  const { t } = useTranslation()

  return (
    <button
      onClick={() => navigate('/home')}
      style={{
        background: 'none',
        border: 'none',
        fontSize: size,
        cursor: 'pointer',
        padding: 0,
        color: '#333',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        ...style
      }}
      title={t('buttons.backToHome')}
    >
      <FaHome size={size} />
    </button>
  )
}

export default HomeButton
