// utils/streakUtils.ts

/**
 * Функция для получения последних 7 дат в локальном формате
 */
export function getLast7LocalDates(): string[] {
  const pad = (n: number) => n.toString().padStart(2, '0')
  const localDateString = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`
  const dates: string[] = []
  
  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    dates.push(localDateString(d))
  }
  
  return dates
}

/**
 * Функция для подсчета текущего streak
 * @param dailyProgress - массив прогресса за последние 7 дней
 * @param dailyGoal - дневная цель
 * @returns количество дней подряд с выполненной целью (считая с конца)
 */
export function calculateCurrentStreak(dailyProgress: number[], dailyGoal: number): number {
  if (!dailyProgress || !dailyGoal || dailyGoal <= 0) return 0
  
  let streak = 0
  
  // Считаем с конца (сегодня)
  for (let i = dailyProgress.length - 1; i >= 0; i--) {
    if (dailyProgress[i] >= dailyGoal) {
      streak++
    } else {
      break // Как только встретили день без выполненной цели, прерываем
    }
  }
  
  return streak
}

/**
 * Функция для подсчета максимального streak за период
 * @param dailyProgress - массив прогресса за последние 7 дней
 * @param dailyGoal - дневная цель
 * @returns максимальный streak за период
 */
export function calculateMaxStreak(dailyProgress: number[], dailyGoal: number): number {
  if (!dailyProgress || !dailyGoal || dailyGoal <= 0) return 0
  
  let maxStreak = 0
  let currentStreak = 0
  
  for (const progress of dailyProgress) {
    if (progress >= dailyGoal) {
      currentStreak++
      maxStreak = Math.max(maxStreak, currentStreak)
    } else {
      currentStreak = 0
    }
  }
  
  return maxStreak
}
