// store/stats.ts - Store for user statistics and daily progress
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UserStats {
  total_questions: number
  answered: number
  correct: number
}

interface DailyProgress {
  questions_mastered_today: number
  date: string
}

interface StatsStore {
  // Data
  userStats: UserStats | null
  dailyProgress: DailyProgress | null
  lastUpdated: number
  
  // Loading states
  isStatsLoading: boolean
  isProgressLoading: boolean
  
  // Actions
  setUserStats: (stats: UserStats) => void
  setDailyProgress: (progress: DailyProgress) => void
  setStatsLoading: (loading: boolean) => void
  setProgressLoading: (loading: boolean) => void
  
  // Optimistic updates
  updateStatsOptimistic: (correctAnswers: number, totalAnswers: number) => void
  updateProgressOptimistic: (questionsAnswered: number) => void
  
  // Data freshness check
  isDataFresh: (maxAgeMinutes?: number) => boolean
  
  // Clear data
  clearStats: () => void
}

export const useStatsStore = create<StatsStore>()(
  persist(
    (set, get) => ({
      // Initial state
      userStats: null,
      dailyProgress: null,
      lastUpdated: 0,
      isStatsLoading: false,
      isProgressLoading: false,
      
      // Set data from server
      setUserStats: (stats) => 
        set({ 
          userStats: stats, 
          lastUpdated: Date.now(),
          isStatsLoading: false 
        }),
      
      setDailyProgress: (progress) => 
        set({ 
          dailyProgress: progress, 
          lastUpdated: Date.now(),
          isProgressLoading: false 
        }),
      
      setStatsLoading: (loading) => set({ isStatsLoading: loading }),
      setProgressLoading: (loading) => set({ isProgressLoading: loading }),
      
      // Optimistic updates for immediate UI feedback
      updateStatsOptimistic: (correctAnswers, totalAnswers) => {
        const currentStats = get().userStats
        if (currentStats) {
          set({
            userStats: {
              ...currentStats,
              answered: currentStats.answered + totalAnswers,
              correct: currentStats.correct + correctAnswers,
            },
            lastUpdated: Date.now()
          })
        }
      },
      
      updateProgressOptimistic: (questionsAnswered) => {
        const today = new Date().toISOString().split('T')[0]
        const currentProgress = get().dailyProgress
        
        set({
          dailyProgress: {
            questions_mastered_today: (currentProgress?.questions_mastered_today || 0) + questionsAnswered,
            date: today
          },
          lastUpdated: Date.now()
        })
      },
      
      // Check if data is fresh (default: 5 minutes)
      isDataFresh: (maxAgeMinutes = 5) => {
        const { lastUpdated } = get()
        const maxAge = maxAgeMinutes * 60 * 1000
        return Date.now() - lastUpdated < maxAge
      },
      
      // Clear all data
      clearStats: () => set({
        userStats: null,
        dailyProgress: null,
        lastUpdated: 0,
        isStatsLoading: false,
        isProgressLoading: false
      })
    }),
    {
      name: 'user-stats-storage',
      // Only persist the data, not loading states
      partialize: (state) => ({
        userStats: state.userStats,
        dailyProgress: state.dailyProgress,
        lastUpdated: state.lastUpdated
      })
    }
  )
)
