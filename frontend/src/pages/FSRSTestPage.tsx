// FSRS Test Page
import React, { useState } from 'react'
import FSRSDashboard from '../components/fsrs/FSRSDashboard'
import { useFSRSActions, useFSRSSettings, useFSRSPendingAnswers } from '../store/fsrs'
import { useSession } from '../store/session'

const FSRSTestPage = () => {
  const { userId } = useSession()
  const settings = useFSRSSettings()
  const pendingAnswers = useFSRSPendingAnswers()
  const { updateSettings, addAnswer, submitPendingAnswers, clearPendingAnswers } = useFSRSActions()

  const [testQuestionId, setTestQuestionId] = useState(1)
  const [isCorrect, setIsCorrect] = useState(true)
  const [responseTime, setResponseTime] = useState(5000)

  const handleAddTestAnswer = () => {
    addAnswer(testQuestionId, isCorrect, responseTime)
    setTestQuestionId(prev => prev + 1)
  }

  const handleSubmitAnswers = async () => {
    if (userId) {
      await submitPendingAnswers(userId)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🧠 FSRS Algorithm Testing
          </h1>
          <p className="text-gray-600">
            Test the Free Spaced Repetition Scheduler integration
          </p>
        </div>

        {/* FSRS Settings */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">⚙️ FSRS Settings</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={settings.enabled}
                onChange={(e) => updateSettings({ enabled: e.target.checked })}
                className="rounded"
              />
              <span>FSRS Enabled</span>
            </label>
            
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={settings.autoRating}
                onChange={(e) => updateSettings({ autoRating: e.target.checked })}
                className="rounded"
              />
              <span>Auto Rating</span>
            </label>
            
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={settings.showIntervals}
                onChange={(e) => updateSettings({ showIntervals: e.target.checked })}
                className="rounded"
              />
              <span>Show Intervals</span>
            </label>
            
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={settings.showStats}
                onChange={(e) => updateSettings({ showStats: e.target.checked })}
                className="rounded"
              />
              <span>Show Stats</span>
            </label>
          </div>
        </div>

        {/* Test Answer Generation */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">🧪 Test Answer Generation</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Question ID
              </label>
              <input
                type="number"
                value={testQuestionId}
                onChange={(e) => setTestQuestionId(parseInt(e.target.value))}
                className="w-full border rounded px-3 py-2"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Answer Correct?
              </label>
              <select
                value={isCorrect.toString()}
                onChange={(e) => setIsCorrect(e.target.value === 'true')}
                className="w-full border rounded px-3 py-2"
              >
                <option value="true">✅ Correct</option>
                <option value="false">❌ Incorrect</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Response Time (ms)
              </label>
              <input
                type="number"
                value={responseTime}
                onChange={(e) => setResponseTime(parseInt(e.target.value))}
                className="w-full border rounded px-3 py-2"
              />
            </div>
          </div>
          
          <button
            onClick={handleAddTestAnswer}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Add Test Answer
          </button>
        </div>

        {/* Pending Answers */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">📝 Pending Answers ({pendingAnswers.length})</h2>
            <div className="space-x-2">
              <button
                onClick={handleSubmitAnswers}
                disabled={!userId || pendingAnswers.length === 0}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
              >
                Submit to FSRS
              </button>
              <button
                onClick={clearPendingAnswers}
                disabled={pendingAnswers.length === 0}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
              >
                Clear Pending
              </button>
            </div>
          </div>
          
          {pendingAnswers.length > 0 ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {pendingAnswers.map((answer, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <div className="flex items-center space-x-3">
                    <span className="font-mono text-sm">Q{answer.questionId}</span>
                    <span className={answer.isCorrect ? 'text-green-600' : 'text-red-600'}>
                      {answer.isCorrect ? '✅' : '❌'}
                    </span>
                    <span className="text-sm text-gray-500">
                      Rating: {answer.rating}
                    </span>
                    {answer.responseTime && (
                      <span className="text-sm text-gray-500">
                        {answer.responseTime}ms
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-gray-400">
                    {new Date(answer.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">
              No pending answers. Add some test answers above.
            </p>
          )}
        </div>

        {/* FSRS Dashboard */}
        {settings.showStats && (
          <FSRSDashboard />
        )}

        {/* User Info */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">👤 User Info</h2>
          {userId ? (
            <div className="space-y-2">
              <p><strong>User ID:</strong> {userId}</p>
              <p><strong>FSRS Enabled:</strong> {settings.enabled ? '✅ Yes' : '❌ No'}</p>
            </div>
          ) : (
            <p className="text-red-500">❌ No user logged in</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default FSRSTestPage
