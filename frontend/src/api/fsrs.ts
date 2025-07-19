// Frontend FSRS API integration
import { z } from 'zod'

// ============================================================================
// FSRS API Types and Schemas
// ============================================================================

export const FSRSRatingSchema = z.number().int().min(1).max(4)
export type FSRSRating = z.infer<typeof FSRSRatingSchema>

export const FSRSStateSchema = z.number().int().min(0).max(3)
export type FSRSState = z.infer<typeof FSRSStateSchema>

export interface FSRSData {
  stability: number
  difficulty: number
  retrievability?: number | null
  state: FSRSState
  reps: number
  lapses: number
  due: string
}

export interface FSRSAnswerSubmission {
  user_id: string
  question_id: number
  is_correct: boolean
  answered_at?: string
}

export interface FSRSBatchAnswerItem {
  question_id: number
  is_correct: boolean
  answered_at: string
}

export interface FSRSBatchSubmission {
  user_id: string
  answers: FSRSBatchAnswerItem[]
}

export interface FSRSProgressResponse {
  message: string
  progress: {
    question_id: number
    is_correct: boolean
    repetition_count: number
    next_due_at: string
    fsrs_data: FSRSData
  }
}

export interface FSRSBatchResponse {
  message: string
  results: Array<{
    question_id: number
    processed: boolean
    fsrs_rating: FSRSRating
    next_due_at: string
    stability: number
    difficulty: number
  }>
}

export interface FSRSInterval {
  interval_days: number
  due_date: string
  stability: number
  difficulty: number
  state: string
}

export interface FSRSIntervals {
  again: FSRSInterval
  hard: FSRSInterval
  good: FSRSInterval
  easy: FSRSInterval
}

export interface FSRSDueQuestion {
  question_id: number
  due_date: string
  days_overdue: number
  fsrs_data: {
    state: string
    stability: number
    difficulty: number
    reps: number
    lapses: number
  }
  predicted_intervals: FSRSIntervals
}

export interface FSRSDueQuestionsResponse {
  total_due: number
  questions: FSRSDueQuestion[]
}

export interface FSRSStats {
  total_cards: number
  due_count: number
  avg_stability: number
  avg_difficulty: number
  state_distribution: Record<string, number>
  state_distribution_named: Record<string, number>
}

export interface FSRSCardInfo {
  question_id: number
  user_id: string
  current_status: {
    is_due: boolean
    due_date: string
    days_until_due: number
    state: string
    stability: number
    difficulty: number
  }
  predicted_intervals: FSRSIntervals
  history: {
    total_reps: number
    total_lapses: number
    last_review: string | null
    created_at: string
  }
  fsrs_params: FSRSData
}

// ============================================================================
// FSRS API Client
// ============================================================================

const FSRS_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://tgapp-backend.onrender.com/fsrs'
  : 'http://localhost:8000/fsrs'

class FSRSApiClient {
  private baseUrl: string

  constructor(baseUrl: string = FSRS_BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * Submit a single answer with FSRS rating
   */
  async submitAnswer(
    answerData: FSRSAnswerSubmission,
    rating: FSRSRating
  ): Promise<FSRSProgressResponse> {
    const response = await fetch(`${this.baseUrl}/submit-answer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...answerData,
        rating
      })
    })

    if (!response.ok) {
      throw new Error(`FSRS API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Submit batch answers with FSRS ratings
   */
  async submitBatchAnswers(
    batchData: FSRSBatchSubmission,
    ratings: FSRSRating[]
  ): Promise<FSRSBatchResponse> {
    if (batchData.answers.length !== ratings.length) {
      throw new Error('Number of answers must match number of ratings')
    }

    const response = await fetch(`${this.baseUrl}/submit-batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...batchData,
        ratings
      })
    })

    if (!response.ok) {
      throw new Error(`FSRS API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Get questions due for review based on FSRS scheduling
   */
  async getDueQuestions(
    userId: string,
    country: string,
    language: string,
    limit: number = 20
  ): Promise<FSRSDueQuestionsResponse> {
    const params = new URLSearchParams({
      country,
      language,
      limit: limit.toString()
    })

    const response = await fetch(`${this.baseUrl}/due-questions/${userId}?${params}`)

    if (!response.ok) {
      throw new Error(`FSRS API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Get FSRS statistics for a user
   */
  async getStats(userId: string): Promise<FSRSStats> {
    const response = await fetch(`${this.baseUrl}/stats/${userId}`)

    if (!response.ok) {
      throw new Error(`FSRS API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Get detailed FSRS information for a specific card
   */
  async getCardInfo(userId: string, questionId: number): Promise<FSRSCardInfo> {
    const response = await fetch(`${this.baseUrl}/card-info/${userId}/${questionId}`)

    if (!response.ok) {
      throw new Error(`FSRS API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }
}

// ============================================================================
// FSRS Rating Helper Functions
// ============================================================================

/**
 * Convert answer correctness and performance to FSRS rating
 */
export function calculateFSRSRating(isCorrect: boolean, responseTime?: number): FSRSRating {
  if (!isCorrect) {
    return 1 // Again - incorrect answer
  }

  // For correct answers, consider response time if available
  if (responseTime !== undefined) {
    // Quick response (< 3 seconds) = Easy
    if (responseTime < 3000) return 4
    // Medium response (3-8 seconds) = Good  
    if (responseTime < 8000) return 3
    // Slow response (> 8 seconds) = Hard
    return 2
  }

  // Default to Good for correct answers without timing data
  return 3
}

/**
 * Get human-readable FSRS state name
 */
export function getFSRSStateName(state: FSRSState): string {
  const stateNames = {
    0: 'New',
    1: 'Learning',
    2: 'Review',
    3: 'Relearning'
  }
  return stateNames[state] || `Unknown(${state})`
}

/**
 * Get human-readable FSRS rating name
 */
export function getFSRSRatingName(rating: FSRSRating): string {
  const ratingNames = {
    1: 'Again',
    2: 'Hard',
    3: 'Good', 
    4: 'Easy'
  }
  return ratingNames[rating] || `Unknown(${rating})`
}

/**
 * Format interval for display
 */
export function formatInterval(days: number): string {
  if (days === 0) return 'Today'
  if (days === 1) return 'Tomorrow'
  if (days < 7) return `${days} days`
  if (days < 30) return `${Math.round(days / 7)} weeks`
  if (days < 365) return `${Math.round(days / 30)} months`
  return `${Math.round(days / 365)} years`
}

// Default export
export const fsrsApi = new FSRSApiClient()
export default fsrsApi
