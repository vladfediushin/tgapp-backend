import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Home, User, BarChart3, Settings } from 'lucide-react'

const BottomNavigation = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()

  const navItems = [
    { id: 'home', icon: Home, label: t('home.home'), path: '/' },
    { id: 'profile', icon: User, label: t('home.profile'), path: '/profile' },
    { id: 'stats', icon: BarChart3, label: t('home.statistics'), path: '/statistics' },
    { id: 'settings', icon: Settings, label: t('home.settings'), path: '/settings' }
  ]

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/' || location.pathname === '/home'
    }
    return location.pathname === path
  }

  return (
    <div style={{
      position: 'fixed',
      bottom: 0,
      left: 0,
      right: 0,
      backgroundColor: 'white',
      borderTop: '1px solid #e5e7eb',
      padding: '8px 16px',
      zIndex: 1000
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-around',
        alignItems: 'center'
      }}>
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => navigate(item.path)}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              padding: '8px',
              borderRadius: '8px',
              transition: 'all 0.2s ease',
              backgroundColor: isActive(item.path) ? '#ecfdf5' : 'transparent',
              color: isActive(item.path) ? '#059669' : '#6b7280',
              border: 'none',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              if (!isActive(item.path)) {
                e.currentTarget.style.color = '#111827'
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive(item.path)) {
                e.currentTarget.style.color = '#6b7280'
              }
            }}
          >
            <item.icon size={24} />
            <span style={{ 
              fontSize: '12px', 
              marginTop: '4px',
              fontWeight: isActive(item.path) ? '500' : '400'
            }}>
              {item.label}
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}

export default BottomNavigation
