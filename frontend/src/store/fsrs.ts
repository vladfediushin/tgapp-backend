// FSRS Store for state management
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import fsrsApi, { 
  FSRSRating, 
  FSRSStats, 
  FSRSDueQuestion, 
  FSRSCardInfo,
  calculateFSRSRating,
  FSRSData,
  FSRSAnswerSubmission,
  FSRSBatchAnswerItem
} from '../api/fsrs'

// ============================================================================
// FSRS Store Types
// ============================================================================

export interface FSRSAnswer {
  questionId: number
  isCorrect: boolean
  rating: FSRSRating
  timestamp: number
  responseTime?: number
}

export interface FSRSSettings {
  enabled: boolean
  autoRating: boolean // Automatically calculate rating based on performance
  showIntervals: boolean // Show predicted intervals to user
  showStats: boolean // Show FSRS statistics
}

interface FSRSStoreState {
  // Settings
  settings: FSRSSettings
  
  // Current session data
  pendingAnswers: FSRSAnswer[]
  dueQuestions: FSRSDueQuestion[]
  currentStats: FSRSStats | null
  
  // UI state
  isLoading: boolean
  lastError: string | null
  
  // Cache
  cardInfoCache: Record<string, FSRSCardInfo>
  lastStatsUpdate: number | null
  lastDueQuestionsUpdate: number | null
}

interface FSRSStoreActions {
  // Settings management
  updateSettings: (settings: Partial<FSRSSettings>) => void
  toggleFSRS: () => void
  
  // Answer management
  addAnswer: (questionId: number, isCorrect: boolean, responseTime?: number) => void
  submitPendingAnswers: (userId: string) => Promise<void>
  clearPendingAnswers: () => void
  
  // Due questions
  loadDueQuestions: (userId: string, country: string, language: string) => Promise<void>
  refreshDueQuestions: (userId: string, country: string, language: string) => Promise<void>
  
  // Statistics
  loadStats: (userId: string) => Promise<void>
  refreshStats: (userId: string) => Promise<void>
  
  // Card info
  getCardInfo: (userId: string, questionId: number) => Promise<FSRSCardInfo>
  
  // Utility
  clearError: () => void
  setLoading: (loading: boolean) => void
}

type FSRSStore = FSRSStoreState & FSRSStoreActions

// ============================================================================
// FSRS Store Implementation
// ============================================================================

export const useFSRSStore = create<FSRSStore>()(
  persist(
    (set, get) => ({
      // Initial state
      settings: {
        enabled: true,
        autoRating: true,
        showIntervals: true,
        showStats: true
      },
      
      pendingAnswers: [],
      dueQuestions: [],
      currentStats: null,
      
      isLoading: false,
      lastError: null,
      
      cardInfoCache: {},
      lastStatsUpdate: null,
      lastDueQuestionsUpdate: null,

      // Settings actions
      updateSettings: (newSettings) => {
        set((state) => ({
          settings: { ...state.settings, ...newSettings }
        }))
      },

      toggleFSRS: () => {
        set((state) => ({
          settings: { ...state.settings, enabled: !state.settings.enabled }
        }))
      },

      // Answer management
      addAnswer: (questionId, isCorrect, responseTime) => {
        const state = get()
        if (!state.settings.enabled) return

        const rating = state.settings.autoRating 
          ? calculateFSRSRating(isCorrect, responseTime)
          : 3 // Default to "Good" if auto-rating disabled

        const answer: FSRSAnswer = {
          questionId,
          isCorrect,
          rating,
          timestamp: Date.now(),
          responseTime
        }

        set((state) => ({
          pendingAnswers: [...state.pendingAnswers, answer]
        }))
      },

      submitPendingAnswers: async (userId) => {
        const state = get()
        if (!state.settings.enabled || state.pendingAnswers.length === 0) {
          return
        }

        set({ isLoading: true, lastError: null })

        try {
          // Convert to FSRS batch format
          const batchAnswers: FSRSBatchAnswerItem[] = state.pendingAnswers.map(answer => ({
            question_id: answer.questionId,
            is_correct: answer.isCorrect,
            answered_at: new Date(answer.timestamp).toISOString()
          }))

          const ratings = state.pendingAnswers.map(answer => answer.rating)

          // Submit to FSRS API
          await fsrsApi.submitBatchAnswers(
            {
              user_id: userId,
              answers: batchAnswers
            },
            ratings
          )

          // Clear pending answers on success
          set({ 
            pendingAnswers: [],
            lastError: null
          })

          // Optionally refresh stats and due questions
          const { refreshStats, refreshDueQuestions } = get()
          // Note: We'll need country/language context for due questions refresh
          
        } catch (error) {
          console.error('Failed to submit FSRS answers:', error)
          set({ 
            lastError: error instanceof Error ? error.message : 'Failed to submit answers'
          })
        } finally {
          set({ isLoading: false })
        }
      },

      clearPendingAnswers: () => {
        set({ pendingAnswers: [] })
      },

      // Due questions management
      loadDueQuestions: async (userId, country, language) => {
        const state = get()
        if (!state.settings.enabled) return

        set({ isLoading: true, lastError: null })

        try {
          const response = await fsrsApi.getDueQuestions(userId, country, language)
          set({ 
            dueQuestions: response.questions,
            lastDueQuestionsUpdate: Date.now(),
            lastError: null
          })
        } catch (error) {
          console.error('Failed to load due questions:', error)
          set({ 
            lastError: error instanceof Error ? error.message : 'Failed to load due questions'
          })
        } finally {
          set({ isLoading: false })
        }
      },

      refreshDueQuestions: async (userId, country, language) => {
        // Force refresh by clearing cache timestamp
        set({ lastDueQuestionsUpdate: null })
        await get().loadDueQuestions(userId, country, language)
      },

      // Statistics management
      loadStats: async (userId) => {
        const state = get()
        if (!state.settings.enabled) return

        // Don't reload if recently updated (within 5 minutes)
        if (state.lastStatsUpdate && Date.now() - state.lastStatsUpdate < 5 * 60 * 1000) {
          return
        }

        set({ isLoading: true, lastError: null })

        try {
          const stats = await fsrsApi.getStats(userId)
          set({ 
            currentStats: stats,
            lastStatsUpdate: Date.now(),
            lastError: null
          })
        } catch (error) {
          console.error('Failed to load FSRS stats:', error)
          set({ 
            lastError: error instanceof Error ? error.message : 'Failed to load statistics'
          })
        } finally {
          set({ isLoading: false })
        }
      },

      refreshStats: async (userId) => {
        // Force refresh by clearing cache timestamp
        set({ lastStatsUpdate: null })
        await get().loadStats(userId)
      },

      // Card info management
      getCardInfo: async (userId, questionId) => {
        const state = get()
        const cacheKey = `${userId}-${questionId}`
        
        // Return cached data if available
        if (state.cardInfoCache[cacheKey]) {
          return state.cardInfoCache[cacheKey]
        }

        try {
          const cardInfo = await fsrsApi.getCardInfo(userId, questionId)
          
          // Cache the result
          set((state) => ({
            cardInfoCache: {
              ...state.cardInfoCache,
              [cacheKey]: cardInfo
            }
          }))

          return cardInfo
        } catch (error) {
          console.error('Failed to get card info:', error)
          throw error
        }
      },

      // Utility actions
      clearError: () => {
        set({ lastError: null })
      },

      setLoading: (loading) => {
        set({ isLoading: loading })
      }
    }),
    {
      name: 'fsrs-store',
      // Only persist settings and non-sensitive state
      partialize: (state) => ({
        settings: state.settings,
        pendingAnswers: state.pendingAnswers.slice(-50), // Keep only last 50 pending answers
      })
    }
  )
)

// ============================================================================
// FSRS Store Selectors
// ============================================================================

export const useFSRSSettings = () => useFSRSStore((state) => state.settings)
export const useFSRSPendingAnswers = () => useFSRSStore((state) => state.pendingAnswers)
export const useFSRSDueQuestions = () => useFSRSStore((state) => state.dueQuestions)
export const useFSRSStats = () => useFSRSStore((state) => state.currentStats)
export const useFSRSLoading = () => useFSRSStore((state) => state.isLoading)
export const useFSRSError = () => useFSRSStore((state) => state.lastError)

// Export hooks for common actions
export const useFSRSActions = () => {
  const store = useFSRSStore()
  return {
    updateSettings: store.updateSettings,
    toggleFSRS: store.toggleFSRS,
    addAnswer: store.addAnswer,
    submitPendingAnswers: store.submitPendingAnswers,
    clearPendingAnswers: store.clearPendingAnswers,
    loadDueQuestions: store.loadDueQuestions,
    refreshDueQuestions: store.refreshDueQuestions,
    loadStats: store.loadStats,
    refreshStats: store.refreshStats,
    getCardInfo: store.getCardInfo,
    clearError: store.clearError
  }
}
