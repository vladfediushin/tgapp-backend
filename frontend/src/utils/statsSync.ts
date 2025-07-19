// utils/statsSync.ts - Utilities for background stats synchronization
import { getUserStats, getDailyProgress } from '../api/api'
import { useStatsStore } from '../store/stats'

/**
 * Background sync of user stats and daily progress
 * Used after completing tests/quizzes
 */
export const backgroundSyncStats = async (userId: string) => {
  const { setUserStats, setDailyProgress } = useStatsStore.getState()
  
  try {
    // Run both requests in parallel
    const [statsResponse, progressResponse] = await Promise.all([
      getUserStats(userId),
      getDailyProgress(userId)
    ])
    
    // Update Zustand store with fresh data
    setUserStats(statsResponse.data)
    setDailyProgress(progressResponse.data)
    
    console.log('✅ Background stats sync completed')
    return { success: true }
  } catch (error) {
    console.error('❌ Background stats sync failed:', error)
    return { success: false, error }
  }
}

/**
 * Load stats from Zustand or API if not fresh
 * Used on page load
 */
export const loadStatsWithCache = async (userId: string) => {
  const { 
    userStats, 
    dailyProgress, 
    isDataFresh, 
    setStatsLoading, 
    setProgressLoading,
    setUserStats,
    setDailyProgress
  } = useStatsStore.getState()
  
  // If data is fresh, return immediately
  if (userStats && dailyProgress && isDataFresh()) {
    console.log('📦 Using cached stats data')
    return { userStats, dailyProgress, fromCache: true }
  }
  
  // Otherwise load from API
  console.log('🔄 Loading fresh stats data')
  setStatsLoading(true)
  setProgressLoading(true)
  
  try {
    const [statsResponse, progressResponse] = await Promise.all([
      getUserStats(userId),
      getDailyProgress(userId)
    ])
    
    setUserStats(statsResponse.data)
    setDailyProgress(progressResponse.data)
    
    return { 
      userStats: statsResponse.data, 
      dailyProgress: progressResponse.data, 
      fromCache: false 
    }
  } catch (error) {
    setStatsLoading(false)
    setProgressLoading(false)
    throw error
  }
}

/**
 * Optimistic update for immediate UI feedback
 * Call this before API request in Repeat.tsx
 */
export const updateStatsOptimistically = (correctAnswers: number, totalAnswers: number) => {
  const { updateStatsOptimistic, updateProgressOptimistic } = useStatsStore.getState()
  
  // Update stats
  updateStatsOptimistic(correctAnswers, totalAnswers)
  
  // Update daily progress (assume all answered questions are "mastered")
  updateProgressOptimistic(correctAnswers)
  
  console.log(`🚀 Optimistic update: +${correctAnswers}/${totalAnswers}`)
}

/**
 * Check if we need to refresh stats data
 */
export const shouldRefreshStats = (maxAgeMinutes = 10) => {
  const { isDataFresh } = useStatsStore.getState()
  return !isDataFresh(maxAgeMinutes)
}
