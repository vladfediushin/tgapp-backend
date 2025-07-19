// src/main.tsx (или index.tsx)
import React, { useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './i18n'
import { useSession } from './store/session'
import i18n from 'i18next'

const Root: React.FC = () => {
  const uiLang = useSession(state => state.uiLanguage)

  useEffect(() => {
    if (uiLang) {
      i18n.changeLanguage(uiLang)
    }
  }, [uiLang])

  return <App key={uiLang} />
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Root />
    </BrowserRouter>
  </React.StrictMode>,
)