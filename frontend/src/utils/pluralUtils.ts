// utils/pluralUtils.ts

/**
 * Функция для получения правильного склонения/множественного числа для streak
 * @param count - количество дней
 * @param t - функция перевода из react-i18next
 * @returns строка с правильным склонением
 */
export function getStreakText(count: number, t: (key: string, options?: any) => string): string {
  if (count === 1) {
    return t('home.streak.days_1', { count })
  }
  
  // Для русского языка: особые правила склонения
  if (t('home.streak.days_2') !== 'home.streak.days_2') { // проверяем, что перевод существует (русский)
    if (count >= 2 && count <= 4) {
      return t('home.streak.days_2', { count })
    } else if (count === 0 || count >= 5) {
      return t('home.streak.days_5', { count })
    }
  }
  
  // Для английского языка: простое правило
  if (count === 0 || count > 1) {
    return t('home.streak.days_other', { count }) || t('home.streak.days_0', { count })
  }
  
  return t('home.streak.days_1', { count })
}
