// frontend/src/pages/Topics.tsx
import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ChevronLeft, BookOpen } from 'lucide-react'
import BottomNavigation from '../components/BottomNavigation'

const topics = ['Знаки', 'Светофоры', 'Разметка', 'Ситуации', 'Парковка']

const Topics = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const goHome = () => {
    navigate('/')
  }

  const handleSelect = (topic: string) => {
    navigate('/repeat', { state: { topic } })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      <div className="flex-1 p-6 pb-24">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={goHome}
            className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            <ChevronLeft size={20} />
            <span className="font-medium">{t('topics.back')}</span>
          </button>
        </div>

        {/* Title */}
        <div className="text-center mb-8">
          <div className="bg-white rounded-full p-4 w-16 h-16 mx-auto mb-4 shadow-lg flex items-center justify-center">
            <BookOpen size={32} className="text-blue-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('topics.title')}</h1>
          <p className="text-gray-600">{t('topics.subtitle')}</p>
        </div>

        {/* Topics Grid */}
        <div className="space-y-4">
          {topics.map((topic, index) => (
            <button
              key={topic}
              onClick={() => handleSelect(topic)}
              className="w-full bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-all duration-200 border border-gray-100 group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="bg-blue-100 rounded-lg p-3 group-hover:bg-blue-200 transition-colors">
                    <div className="w-6 h-6 bg-blue-600 rounded text-white text-sm font-bold flex items-center justify-center">
                      {index + 1}
                    </div>
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-gray-900 text-lg">{t(`topics.list.${topic}`)}</h3>
                    <p className="text-gray-500 text-sm">{t('topics.clickToStart')}</p>
                  </div>
                </div>
                <ChevronLeft size={20} className="text-gray-400 rotate-180 group-hover:text-blue-600 transition-colors" />
              </div>
            </button>
          ))}
        </div>
      </div>

      <BottomNavigation />
    </div>
  )
}

export default Topics