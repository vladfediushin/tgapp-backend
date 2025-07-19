// FSRS Dashboard Component
import React, { useEffect, useState } from 'react'
import { useFSRSStore, useFSRSStats, useFSRSLoading, useFSRSError, useFSRSActions } from '../../store/fsrs'
import { useSession } from '../../store/session'
import { getFSRSStateName, formatInterval } from '../../api/fsrs'

interface FSRSDashboardProps {
  className?: string
}

const FSRSDashboard = ({ className = '' }: FSRSDashboardProps) => {
  const { cachedUser: user, userId } = useSession()
  const stats = useFSRSStats()
  const isLoading = useFSRSLoading()
  const error = useFSRSError()
  const { loadStats, refreshStats, clearError } = useFSRSActions()

  const [autoRefresh, setAutoRefresh] = useState(false)

  useEffect(() => {
    if (userId) {
      loadStats(userId)
    }
  }, [userId, loadStats])

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      if (userId) {
        refreshStats(userId)
      }
    }, 30000) // Refresh every 30 seconds

    return () => clearInterval(interval)
  }, [autoRefresh, userId, refreshStats])

  const handleRefresh = () => {
    if (userId) {
      refreshStats(userId)
    }
  }

  if (!userId) {
    return (
      <div className={`p-4 text-center ${className}`}>
        <p className="text-gray-500">Please log in to view FSRS statistics</p>
      </div>
    )
  }

  return (
    <div className={`p-6 bg-white rounded-lg shadow-md ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">
          📊 FSRS Statistics
        </h2>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            Auto-refresh
          </label>
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {isLoading ? '⏳' : '🔄'}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded-md">
          <div className="flex items-center justify-between">
            <span className="text-red-700">❌ {error}</span>
            <button
              onClick={clearError}
              className="text-red-500 hover:text-red-700"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && !stats && (
        <div className="text-center py-8">
          <div className="animate-spin text-4xl mb-2">⏳</div>
          <p className="text-gray-500">Loading FSRS statistics...</p>
        </div>
      )}

      {/* Statistics Display */}
      {stats && (
        <div className="space-y-6">
          {/* Overview Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{stats.total_cards}</div>
              <div className="text-sm text-blue-500">Total Cards</div>
            </div>
            
            <div className="p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{stats.due_count}</div>
              <div className="text-sm text-green-500">Due for Review</div>
            </div>
            
            <div className="p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{stats.avg_stability}</div>
              <div className="text-sm text-purple-500">Avg Stability</div>
            </div>
            
            <div className="p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">{stats.avg_difficulty}</div>
              <div className="text-sm text-orange-500">Avg Difficulty</div>
            </div>
          </div>

          {/* State Distribution */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-3">📈 Card States Distribution</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(stats.state_distribution_named).map(([stateName, count]) => (
                <div key={stateName} className="flex items-center justify-between p-2 bg-white rounded">
                  <span className="text-sm font-medium">{stateName}</span>
                  <span className="text-lg font-bold text-gray-700">{count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Progress Insights */}
          <div className="bg-gradient-to-r from-blue-50 to-green-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">🎯 Learning Insights</h3>
            <div className="space-y-2 text-sm">
              {stats.due_count > 0 ? (
                <p className="text-green-700">
                  ✅ You have <strong>{stats.due_count}</strong> cards ready for review
                </p>
              ) : (
                <p className="text-blue-700">
                  🎉 No cards due for review right now!
                </p>
              )}
              
              {stats.avg_stability > 0 && (
                <p className="text-purple-700">
                  📚 Your average card stability is <strong>{stats.avg_stability} days</strong>
                </p>
              )}
              
              {stats.avg_difficulty > 0 && (
                <p className="text-orange-700">
                  🎲 Average difficulty level: <strong>{stats.avg_difficulty.toFixed(1)}/10</strong>
                </p>
              )}
            </div>
          </div>

          {/* Last Updated */}
          <div className="text-xs text-gray-500 text-center">
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      )}

      {/* No Data State */}
      {!isLoading && !stats && !error && (
        <div className="text-center py-8">
          <div className="text-4xl mb-2">📝</div>
          <p className="text-gray-500">No FSRS data available yet.</p>
          <p className="text-sm text-gray-400">Start answering questions to see your statistics!</p>
        </div>
      )}
    </div>
  )
}

export default FSRSDashboard
