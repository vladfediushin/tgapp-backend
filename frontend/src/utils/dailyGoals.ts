// src/utils/dailyGoal.ts - Только чистые функции расчета

export interface DailyGoalData {
  dailyGoal: number
  totalQuestions: number
  alreadyCorrect: number
  remainingQuestions: number
  daysUntilExam: number
  learningDays: number
  isCalculated: boolean
}

export interface TodayProgress {
  questionsMasteredToday: number
  goalProgress: number // 0-100%
  goalMet: boolean
}

/**
 * Основная функция расчета дневной цели
 * Использует данные, которые УЖЕ получены из API
 */
export function calculateDailyGoal(
  examDate: string | null,
  totalQuestions: number,
  alreadyCorrectCount: number 
): DailyGoalData | null {
  
  if (!examDate) {
    return null
  }

  const today = new Date()
  const exam = new Date(examDate)
  const daysUntilExam = Math.max(0, Math.ceil((exam.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)))
  
  const remainingQuestions = Math.max(0, totalQuestions - alreadyCorrectCount)
  
  if (remainingQuestions === 0) {
    return {
      dailyGoal: 0,
      totalQuestions,
      alreadyCorrect: alreadyCorrectCount,
      remainingQuestions: 0,
      daysUntilExam,
      learningDays: 0,
      isCalculated: true
    }
  }

  // 80% времени на изучение, 20% на повторение
  const learningDays = Math.max(1, Math.floor(daysUntilExam * 0.8))
  const dailyGoal = Math.max(1, Math.ceil(remainingQuestions / learningDays))

  return {
    dailyGoal,
    totalQuestions,
    alreadyCorrect: alreadyCorrectCount,
    remainingQuestions,
    daysUntilExam,
    learningDays,
    isCalculated: true
  }
}

/**
 * Расчет прогресса за сегодня
 * Считаем только уникальные правильно отвеченные вопросы за день
 */
export function calculateTodayProgress(
  sessionsAnswers: Array<{ questionId: number; isCorrect: boolean }>, // Из useSession
  dailyGoal: number
): TodayProgress {
  
  // Берем только правильные ответы и делаем уникальными по questionId
  const uniqueCorrectToday = new Set(
    sessionsAnswers
      .filter(a => a.isCorrect)
      .map(a => a.questionId)
  ).size

  const goalProgress = dailyGoal > 0 ? Math.min((uniqueCorrectToday / dailyGoal) * 100, 100) : 0
  const goalMet = uniqueCorrectToday >= dailyGoal

  return {
    questionsMasteredToday: uniqueCorrectToday,
    goalProgress,
    goalMet
  }
}